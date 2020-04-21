import sys
import threading
import time
import zmq
import numpy as np
from collections import OrderedDict
import os
import shelve
import traceback
import scipy.linalg as LA
import pickle
import zlib
import logging
import copy
from numpy.linalg import norm

logging.basicConfig()

try:
    from Telescope import FEM, WindLoad
except:
    logging.warning('Telescope package not found!')


SIMCEOPATH = os.path.abspath(os.path.dirname(__file__))

class testComm:
    def __init__(self):
        pass
    def hello(self,N=1):
        data = np.ones(N)
        return dict(data=data.tolist())

class Timer(object):
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.tstart = time.time()

    def __exit__(self, type, value, traceback):
        if self.name:
            print('[%s]' % self.name)
        print('Elapsed time: %s' % (time.time() - self.tstart))

from abc import ABCMeta, abstractmethod

class Sfunction:
    __metaclass__ = ABCMeta
    @abstractmethod
    def Start(self):
        pass
    @abstractmethod
    def Terminate(self):
        pass
    @abstractmethod
    def Update(self):
        pass
    @abstractmethod
    def Outputs(self):
        pass
    @abstractmethod
    def InitializeConditions(self):
        pass

try:
    import ceo

    class CalibrationMatrix(object):

        def __init__(self, D, n, 
                     decoupled=True, flux_filter2=None,
                     n_mode = None):
            print("@(CalibrationMatrix)> Computing the SVD and the pseudo-inverse...")
            self._n = n
            self.decoupled = decoupled
            if self.decoupled:
                self.nSeg = 7
                self.D = D
                D_s = [ np.concatenate([D[0][:,k*3:k*3+3],
                                        D[1][:,k*3:k*3+3],
                                        D[2][:,k*3:k*3+3],
                                        D[3][:,k*3:k*3+3],
                                        D[4][:,k*n_mode:k*n_mode+n_mode]],axis=1) for k in range(self.nSeg)]
                for k in range(7):
                    D_s[k][np.isnan(D_s[k])] = 0
                lenslet_array_shape = flux_filter2.shape

                ### Identification process
                # The non-zeros entries of the calibration matrix are identified by filtering out all the values 
                # which are a 1000 less than the maximum of the absolute values of the matrix and 
                # collapsing (summing) the matrix along the mirror modes axis.
                Qxy = [ np.reshape( np.sum(np.abs(D_s[k])>1e-2*np.max(np.abs(D_s[k])),axis=1)!=0 ,flux_filter2.shape ) for k in range(self.nSeg) ]
                # The lenslet flux filter is applied to the lenslet segment filter:
                Q = [ np.logical_and(X,flux_filter2) for X in Qxy ]
                # A filter made of the lenslet used more than once is created:
                Q3 = np.dstack(Q).reshape(flux_filter2.shape + (self.nSeg,))
                Q3clps = np.sum(Q3,axis=2)
                Q3clps = Q3clps>1
                # The oposite filter is applied to the lenslet segment filter leading to 7 valid lenslet filters, 
                # one filter per segment and no lenslet used twice:
                self.VLs = [ np.logical_and(X,~Q3clps) for X in Q] 

                # Each calibration matrix is reduced to the valid lenslet:
                D_sr = [ D_s[k][self.VLs[k].ravel(),:] for k in range(self.nSeg) ]
                print([ D_sr[k].shape for k in range(self.nSeg)])
                # Computing the SVD for each segment:
                self.UsVT = [LA.svd(X,full_matrices=False) for X in D_sr]

                # and the command matrix of each segment
                self.M = [ self.__recon__(k) for k in range(self.nSeg) ]
            else:
                self.D = np.concatenate( D, axis=1 )
                with Timer():
                    self.U,self.s,self.V = LA.svd(self.D,full_matrices=False)
                    self.V = self.V.T
                    iS = 1./self.s
                    if self._n>0:
                        iS[-self._n:] = 0
                    self.M = np.dot(self.V,np.dot(np.diag(iS),self.U.T))
                
        def __recon__(self,k):
            iS = 1./self.UsVT[k][1]
            if self._n>0:
                iS[-self._n:] = 0
            return np.dot(self.UsVT[k][2].T,np.dot(np.diag(iS),self.UsVT[k][0].T))
                
        @property
        def nThreshold(self):
            "# of discarded eigen values"
            return self._n
        @nThreshold.setter
        def nThreshold(self, value):
            print("@(CalibrationMatrix)> Updating the pseudo-inverse...")
            self._n = value
            if self.decoupled:
                self.M = [ self.__recon__(k) for k in range(self.nSeg) ]
            else:
                iS = 1./self.s
                if self._n>0:
                    iS[-self._n:] = 0
                self.M = np.dot(self.V,np.dot(np.diag(iS),self.U.T))

        def dot( self, s ):
            if self.decoupled:
                return np.concatenate([ np.dot(self.M[k],s[self.VLs[k].ravel()]) for k in range(self.nSeg) ])
            else:
                return np.dot(self.M,s)
    class SGMT(Sfunction):

        def __init__(self, ops, satm, verbose=logging.INFO):
            self.logger = logging.getLogger(self.__class__.__name__)
            self.logger.setLevel(verbose)
            self.logger.info('Instantiate')
            self.gmt  = ceo.GMT_MX()
            self.state0 = copy.deepcopy(self.gmt.state)

        def Terminate(self, args=None):
            self.logger.info('Terminate')
            self.gmt = ceo.GMT_MX()
            return "GMT deleted!"
        def Start(self,mirror=None,mirror_args={}):
            self.logger.info('Start')
            if mirror_args:
                self.gmt[mirror] = getattr(ceo,"GMT_"+mirror)( **mirror_args )
                self.state0 = copy.deepcopy(self.gmt.state)
            return "GMT"
        def Update(self, mirror=None, inputs=None):
            self.logger.debug("Updating %s", mirror)
            state = self.gmt.state
            for dof in inputs:
                if dof=='Rxy':
                    data = np.zeros((7,3))
                    data[:,:2] = np.asarray( inputs[dof], order='C', dtype=np.float64 )
                    dof = 'Rxyz'
                elif dof=='Tz':
                    data = np.zeros((7,3))
                    data[:,2] = np.ravel(np.asarray( inputs[dof], order='C', dtype=np.float64 ))
                    dof = 'Txyz'
                else:
                    data = np.asarray( inputs[dof], order='C', dtype=np.float64 )
                #data = np.transpose( np.reshape( data , (-1,7) ) )
                self.logger.debug(" . DOF: %s=|%s|", dof, np.array_str(norm(data,axis=1)))
                state[mirror][dof][:] = self.state0[mirror][dof][:] + data
                """
                if key=="TxyzRxyz":
                    state[mirror]['Txyz'][:] += data[:,:3].copy()
                    state[mirror]['Rxyz'][:] += data[:,3:].copy()
                elif key=="Rxy":
                    state[mirror]['Rxyz'][:,:2] += data.copy()
                elif key=="Tz":
                    state[mirror]['Txyz'][:,2] += data.ravel().copy()
                elif key=="mode_coefs":
                    state[mirror]['modes'][:] += data.copy()
                """
            self.logger.debug('GMT STATE: %s',state)
            self.gmt^=state
        def Init(self, state={}):
            for mirror in state:
                self.state0[mirror].update(state[mirror])
                self.logger.info("GMT state set to %s",self.state0)
        def Outputs(self, args=None):
            pass
    class _Atmosphere_():
        def __init__(self,**kwargs):
            print(kwargs)
            self.__atm = ceo.GmtAtmosphere(**kwargs)
            self.N = kwargs['NXY_PUPIL']
            self.L = kwargs['L']
            self.delta = self.L/(self.N-1)
        def propagate(self,src):
            self.__atm.ray_tracing(src,self.delta,self.N,self.delta,self.N,src.timeStamp)
    class SAtmosphere(Sfunction):

        def __init__(self, ops, verbose=logging.INFO):
            self.logger = logging.getLogger(self.__class__.__name__)
            self.logger.setLevel(verbose)
            self.atm = None

        def Start(self, **kwargs):
            print("\n@(SAtmosphere:Start)>")
            #self.atm = _Atmosphere_( **kwargs )
            self.atm = ceo.GmtAtmosphere(**kwargs)
            return "ATM"

        def Terminate(self, args=None):
            self.logger.info("Atmosphere deleted")
            self.atm = None
            return "Atmosphere deleted!"

        def InitializeConditions(self, args=None):
            pass

        def Outputs(self, args=None):
            pass

        def Update(self, args=None):
            pass
    class SOpticalPath(Sfunction):

        def __init__(self, idx, gmt, atm, verbose=logging.INFO):
            self.logger = logging.getLogger(self.__class__.__name__)
            self.logger.setLevel(verbose)
            self.logger.info('Instantiate')
            self.idx = idx
            self.gmt = gmt
            self.atm = atm
            self.sensor = None
        def Start(self,source_args=None, source_attributes={},
                  sensor_class=None, sensor_args=None,
                  calibration_source_args=None, calibrate_args=None):
            self.pssn_data = None
            #self.propagateThroughAtm = miscellaneous_args['propagate_through_atmosphere']
            self.logger.info('Instantiating source')
            self.src = ceo.Source( **source_args )
            for key in source_attributes:
                attr = source_attributes[key]
                if isinstance(attr,dict):
                    for kkey in attr:
                        setattr(getattr(self.src,key),kkey,attr[kkey])
                else:
                    setattr(self.src,key,attr)
            self.src.reset()
            self.gmt.reset()
            self.gmt.propagate(self.src)
            self.sensor_class = sensor_class
            
            if not (sensor_class is None or sensor_class=='None'):

                self.logger.info('Instantiating sensor')
                self.logger.debug(sensor_class)
                self.logger.debug(sensor_args)
                self.sensor = getattr(ceo,sensor_class)( **sensor_args )
                if calibration_source_args is None:
                    self.calib_src = self.src
                else:
                    self.calib_src = ceo.Source( **calibration_source_args )
            
                self.sensor.reset()
                if calibrate_args is not None:
                    self.sensor.calibrate(self.calib_src, **calibrate_args)
                #print "intensity_threshold: %f"%sensor_args['intensityThreshold']

                self.sensor.reset()
                self.comm_matrix = {}

            self.src>>tuple(filter(None,(self.atm,self.gmt,self.sensor)))

            return "OP"+str(self.idx)
        def Terminate(self, args=None):
            self.logger.info("OpticalPath deleted")
            return "OpticalPath deleted!"
        def Update(self, inputs=None):
            self.logger.debug('src time stamp: %f',self.src.timeStamp)
            +self.src
            #self.src.reset()
            #self.gmt.propagate(self.src)
            #self.sensor.propagate(self.src)
        def Outputs(self, outputs=None):
            if self.sensor is None:
                doutputs = OrderedDict()
                for element in outputs:
                    doutputs[element] = self[element]
            else:
                #+self.sensor
                try:
                    self.sensor.camera.readOut(self.sensor.camera.exposureTime,
                                               self.sensor.camera.readOutNoiseRms,
                                               self.sensor.camera.nBackgroundPhoton,
                                               self.sensor.camera.noiseFactor)
                except:
                    pass
                self.sensor.process()
                doutputs = OrderedDict()
                for element in outputs:
                    doutputs[element] = self[element]
                self.sensor.reset()
            return doutputs
        def __getitem__(self,key):
            if key=="wfe_rms":
                return self.src.wavefront.rms()
            elif key=="segment_wfe_rms":
                return self.src.phaseRms(where="segments")
            elif key=="piston":
                return self.src.piston(where="pupil")
            elif key=="segment_piston":
                return self.src.piston(where="segments")
            elif key=="tiptilt":
                return self.src.wavefront.gradientAverage(1,self.src.rays.L)
            elif key=="segment_tiptilt":
                return self.src.segmentsWavefrontGradient().T
            elif key=="ee80":
                #print "EE80=%.3f or %.3f"%(self.sensor.ee80(from_ghost=False),self.sensor.ee80(from_ghost=True))
                return self.sensor.ee80(from_ghost=False)
            elif key=="PSSn":
                if self.pssn_data is None:
                    pssn , self.pssn_data = self.gmt.PSSn(self.src,save=True)
                else:
                    pssn = self.gmt.PSSn(self.src,**self.pssn_data)
                return pssn
            elif hasattr(self.src,key):
                return getattr(self.src,key)
            elif hasattr(self.sensor,key):
                return getattr(self.sensor,key)
            else:
                c = self.comm_matrix[key].dot( self.sensor.Data ).ravel()
                return c
        def Init(self, calibrations=None, filename=None,
             pseudo_inverse={}):
            self.logger.info('INIT')
            if calibrations is not None:
                if filename is not None:
                    filepath = os.path.join(SIMCEOPATH,"calibration_dbs",filename)
                    db = shelve.open(filepath)
                    
                    if os.path.isfile(filepath+".dir"):
                        self.logger.info("Loading command matrix from existing database %s!",filename)
                        for key in db:
                            C = db[key]
                            #C.nThreshold = [SVD_truncation[k]]
                            self.comm_matrix[key] = C
                            db[key] = C
                        db.close()
                        return
                    
                with Timer():
                    for key in calibrations: # Through calibrations
                        self.logger.info('Calibrating: %s',key)
                        calibs = calibrations[key]
                        #Gif not isinstance(calibs,list):
                        #    calibs = [calibs]
                        #GD = []
                        #for c in calibs: # Through calib
                        self.gmt.reset()
                        self.src.reset()
                        self.sensor.reset()
                        if calibs["method_id"]=="AGWS_calibrate":
                            C = getattr( self.gmt, calibs["method_id"] )( \
                                            self.sensor, 
                                            self.src,
                                            **calibs["args"],
                                            calibrationVaultKwargs=pseudo_inverse)
                        else:
                            D = getattr( self.gmt, calibs["method_id"] )( \
                                            self.sensor, 
                                            self.src,
                                            **calibs["args"])
                            C = ceo.CalibrationVault([D],**pseudo_inverse)
                        self.gmt.reset()
                        self.src.reset()
                        self.sensor.reset()
                        self.comm_matrix[key] = C


                if filename is not None:
                    self.logger.info("Saving command matrix to database %s!",filename)
                    db[str(key)] = C
                    db.close()
    class SEdgeSensors(Sfunction):

        def __init__(self, gmt, verbose=logging.INFO):
            self.logger = logging.getLogger(self.__class__.__name__)
            self.logger.setLevel(verbose)
            self.logger.info('Instantiate')
            self.gmt = gmt

        def Start(self,**kwargs):
            self.es = ceo.DistanceEdgeSensors(self.gmt.M1,**kwargs)
            self.comm_matrix = {}
            return "EdgeSensors"
        def Terminate(self,*args,**kwargs): 
            self.logger.info("EdgeSensors deleted")
            del(self.es)
            return "EdgeSensors deleted!"
        def Update(self,*args,**kwargs): 
            self.es.data()
        def Outputs(self,outputs=['deltas']):
            return {outputs[0]:self.es.d}
        def Init(self,
                 calibrations=None,
                 filename=None,
                 pseudo_inverse={}):
            self.logger.info('INIT')

            state0 = self.gmt.state
            self.gmt.reset()
            (self.gmt)^=state0

            error_1sig_per_m = self.es.error_1sig_per_m
            self.es.error_1sig_per_m = 0.0
            self.es.calibration()
            self.es.error_1sig_per_m = error_1sig_per_m

            if filename is not None:
                filepath = os.path.join(SIMCEOPATH,"calibration_dbs",filename)
                db = shelve.open(filepath)

                if os.path.isfile(filepath+".dir"):
                    self.logger.info("Loading command matrix from existing database %s!",filename)
                    for key in db:
                        C = db[key]
                        self.comm_matrix[key] = C
                        db[key] = C
                    db.close()
                    return

            with Timer():
                for key in calibrations: # Through calibrations
                    self.logger.info('Calibrating: %s',key)
                    calibs = calibrations[key]
                    print('calibs',calibs)
                    stroke = calibs['args']['stroke']
                    state0 = self.gmt.state
                    self.gmt.reset()
                    error_1sig_per_m = self.es.error_1sig_per_m
                    self.es.error_1sig_per_m = 0.0
                    De = []
                    for mirror in ['M1']:
                        for seg in range(6):
                            print(seg,end='')
                            for mode in ['Txyz','Rxyz']:
                                print(mode,end='')
                                for axis in range(3):
                                    print(axis,end='')
                                    self.gmt.reset()
                                    state = self.gmt.state
                                    state[mirror][mode][seg,axis] = stroke
                                    (self.gmt)^=state
                                    self.es.data()
                                    dp = self.es.d
                                    self.gmt.reset()
                                    state = self.gmt.state
                                    state[mirror][mode][seg,axis] = -stroke
                                    (self.gmt)^=state
                                    self.es.data()
                                    dm = self.es.d
                                    De += [0.5*(dp-dm)]
                            print('')
                    De = np.hstack(De)/stroke
                    print('pseudo_inverse',pseudo_inverse)
                    C = ceo.CalibrationVault([De],**pseudo_inverse)
                    (self.gmt)^=state0
                    self.es.error_1sig_per_m = error_1sig_per_m

                    if filename is not None:
                        self.logger.info("Saving command matrix to database %s!",filename)
                        db[str(key)] = C
                        db.close()
except ModuleNotFoundError:
    print("WARNING: CEO is not available on that machine!")

class broker(threading.Thread):

    def __init__(self, verbose=logging.INFO):

        threading.Thread.__init__(self)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.verbose = verbose
        self.logger.setLevel(self.verbose)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.address = "tcp://*:3650"
        self.socket.bind(self.address)
        self.loop = True
        
        self.ops = []
        self.n_op = 0
        self.currentTime = 0.0
        try:
            self.satm = SAtmosphere(self.ops,verbose=self.verbose)
            self.sgmt = SGMT(self.ops, self.satm, verbose=self.verbose)
        except:
            pass

    def __del__(self):

        self.release()

    def release(self):

        self.socket.close()
        self.context.term()

    def _send_(self,obj,protocol=-1,flags=0):
        pobj = pickle.dumps(obj,protocol)
        zobj = zlib.compress(pobj)
        self.socket.send(zobj, flags=flags)

    def _recv_(self,flags=0):
        zobj = self.socket.recv(flags)
        pobj = zlib.decompress(zobj)
        return pickle.loads(pobj)

    def __getitem__(self,key):
        if key=="GMT":
            return self.sgmt
        elif key=="ATM":
            return self.satm
        elif key[:2]=="OP":
            if key[2:]:
                op_idx = int(key[2:]) - self.n_op + len(self.ops)
                return self.ops[op_idx]
            else:
                self.ops.append( SOpticalPath( len(self.ops) ,
                                               self.sgmt.gmt ,
                                               self.satm.atm ,
                                               verbose=self.verbose) )            
                self.n_op = len(self.ops)
                return self.ops[-1]
        elif key=='testComm':
            return testComm()
        elif key=="FEM":
            if not hasattr(self,'fem'):
                self.fem = FEM()
            return self.fem
        elif key=="WindLoad":
            if not hasattr(self,'winds'):
                self.winds = WindLoad()
            return self.winds
        elif key=="EdgeSensors":
            if not hasattr(self,'ses'):
                self.ses = SEdgeSensors(self.sgmt.gmt)
            return self.ses
        else:
            raise KeyError("Available keys are: GMT, ATM or OP")

    def run(self):
        
        while self.loop:

            #jmsg = ubjson.loadb(msg)
            msg = ''
            try:
                self.logger.debug('Waiting for message ...')
                #msg = self.socket.recv()
                #jmsg = ubjson.loadb(msg)
                msg = self._recv_()
                self.logger.debug('Received: %s',msg)
            except Exception as E:
                #print("Error raised by ubjson.loadb by that does not stop us!")
                print(msg)
                raise
            #self.currentTime = float( jmsg["currentTime"][0][0] )
            if not 'class_id' in msg:
                self._send_("SIMCEO server received: {}".format(msg))
                continue
            class_id  = msg["class_id"]
            method_id = msg["method_id"]
            self.logger.debug('Calling out: %s.%s',class_id,method_id)
            #print "@ %.3fs: %s->%s"%(currentTime,jmsg["tag"],method_id)
            #tid = ceo.StopWatch()
            try:
                #tid.tic()
                args_out = getattr( self[class_id], method_id )( **msg["args"] )
                #tid.toc()
                #print "%s->%s: %.2f"%(class_id,method_id,tid.elapsedTime) 
            except Exception as E:
                print("@(broker)> The server has failed!")
                print(msg)
                traceback.print_exc()
                print("@(broker)> Recovering gracefully...")
                class_id = ""
                args_out = "The server has failed!"
            if method_id=="Terminate":
                if class_id[:2]=="OP":
                    self.ops.pop(0)
                elif class_id=="EdgeSensors":
                    delattr(self,'ses')
            #self.socket.send(ubjson.dumpb(args_out,no_float32=True))
            self._send_(args_out)

if __name__ == "__main__":

    print("*********************************")
    print("**   STARTING SIMCEO SERVER    **")
    print("*********************************")
    args = sys.argv[1:]
    verbose = int(args[0]) if args else logging.INFO
    agent = broker(verbose=verbose)
    agent.start()
 

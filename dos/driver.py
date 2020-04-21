import numpy as np
from ruamel.yaml import YAML
yaml=YAML(typ='safe')
import logging
import pandas as pd
from numpy.linalg import norm
from dos import control
logging.basicConfig()
class IO:
    def __init__(self,tag,size=0, lien=None, logs=None):
        self.logger = logging.getLogger(tag)
        self.logger.setLevel(logging.INFO)
        self.size = size
        self.data = np.zeros(size)
        self.lien = lien
        self.logs = logs
class Input(IO):
    def __init__(self,*args,**kwargs):
        IO.__init__(self,*args,**kwargs)
    def tie(self,drivers):
        if self.lien is not None:
            d,io = self.lien
            self.logger.info('Linked to %s from %s',io,d)
            self.data = drivers[d].outputs[io].data
            self.size = self.data.shape
class Output(IO):
    def __init__(self,*args,sampling_rate=1,**kwargs):
        IO.__init__(self,*args,**kwargs)
        self.sampling_rate = sampling_rate
    def tie(self,drivers):
        if self.lien is not None:
            d,io = self.lien
            self.logger.info('Linked to %s from %s',io,d)
            self.data = drivers[d].inputs[io].data
            self.size = self.data.shape
class Driver:
    def __init__(self,tau,tag):
        self.tau = tau
        self.tag = tag
        self.delay = 0
        self.sampling_rate = 1
    def start(self):
        pass
    def init(self):
        pass
    def update(self,_):
        pass
    def output(self,_):
        pass
    def terminate(self):
        pass
class Server(Driver):
    def __init__(self,tau,tag,logs,server,delay=0,sampling_rate=1,
             verbose=logging.INFO,**kwargs):
        Driver.__init__(self,tau,tag)
        self.logger = logging.getLogger(tag)
        self.logger.setLevel(verbose)
        self.delay         = delay
        self.sampling_rate = sampling_rate
        self.inputs       = {}
        try:
            for k in kwargs['inputs']:
                v = kwargs['inputs'][k]
                self.logger.info('New input: %s',k)
                self.inputs[k] = Input(k,**v)
        except KeyError:
            self.logger.info('No inputs!')
        self.outputs       = {}
        try:
            for k in kwargs['outputs']:
                v = kwargs['outputs'][k]
                self.logger.info('New output: %s',k)
                if not 'sampling_rate' in v:
                    v['sampling_rate']=self.sampling_rate
                if v['sampling_rate']<self.sampling_rate:
                    if v['sampling_rate']!=1:
                        self.logger.error('The driver output rate cannot be less than the update rate!')
                    self.logger.warning('Changing the output rate to match the update rate!')
                    v['sampling_rate'] = self.sampling_rate
                if 'logs' in v:
                    logs.add(tag,k,v['logs']['decimation'],self.delay)
                    if v['logs']['decimation']<v['sampling_rate']:
                        if v['logs']['decimation']!=1:
                            self.logger.error('The log decimation rate cannot be less than the output rate!')
                        self.logger.warning('Changing the decimation rate to match the output rate!')
                        v['logs']['decimation'] = v['sampling_rate']
                    v['logs'] = logs.entries[tag][k]
                    self.logger.info('Output logged in!')
                self.outputs[k] = Output(k,**v)
        except KeyError:
            self.logger.info('No inputs!')
        try:
            self.shape = kwargs['shape']
        except KeyError:
            self.shape = None
        try:
            self.split = kwargs['split']
        except KeyError:
            self.split = {'indices_or_sections':1,'axis':0}
        self.server        = server
        self.msg = {'class_id':'',
                    'method_id':'',
                    'args':{}}
        self.msg_args = {'Start':{},
                    'Init':{},
                    'Update':{'inputs':{}},
                    'Outputs':{'outputs':[]},
                    'Terminate':{'args':None}}

    def start(self):
        self.logger.debug('Starting!')
        m = 'Start'
        self.msg['method_id'] = m
        self.msg['args'].update(self.msg_args[m])
        self.server._send_(self.msg)
        self.msg['method_id'] = ''
        self.msg['args'].clear()
        reply = self.server._recv_()
        self.msg['class_id'] = reply
        self.logger.info('%s',reply)
    def init(self):
        self.logger.debug('Initializing!')
        m = 'Init'
        self.msg['method_id'] = m
        self.msg['args'].update(self.msg_args[m])
        self.server._send_(self.msg)
        self.msg['method_id'] = ''
        self.msg['args'].clear()
        reply = self.server._recv_()
        self.logger.info('%s',reply)
    def update(self,step):
        if step>=self.delay and (step-self.delay)%self.sampling_rate==0:
            self.logger.debug('Updating!')
            m = 'Update'
            self.msg['method_id'] = m
            self.msg['args'].update(self.msg_args[m])
            self.server._send_(self.msg)
            self.msg['method_id'] = ''
            self.msg['args'].clear()
            reply = self.server._recv_()
    def output(self,step):
        if step>=self.delay:
                m = 'Outputs'
                if self.msg_args[m]['outputs']:
                    self.msg['method_id'] = m
                    self.msg['args'].update(self.msg_args[m])
                    self.server._send_(self.msg)
                    self.msg['method_id'] = ''
                    self.msg['args'].clear()
                    reply = self.server._recv_()
                    #self.logger.debug("Reply: %s",reply)
                    for k,v in self.outputs.items():
                        if (step-self.delay)%v.sampling_rate==0:
                            self.logger.debug('Outputing %s!',k)
                            try:
                                v.data[...] = np.asarray(reply[k]).reshape(v.size)
                            except ValueError:
                                self.logger.warning('Resizing %s!',k)
                                __red = np.asarray(reply[k])
                                v.size = __red.shape
                                v.data = np.zeros(__red.shape)
                                v.data[...] = __red
                            if v.logs is not None and (step-self.delay)%v.logs.decimation==0:
                                self.logger.debug('LOGGING')
                                v.logs.add(v.data.copy())

    def terminate(self):
        self.logger.debug('Terminating!')
        m = 'Terminate'
        self.msg['method_id'] = m
        self.msg['args'].update(self.msg_args[m])
        self.server._send_(self.msg)
        self.msg['method_id'] = ''
        self.msg['args'].clear()
        reply = self.server._recv_()
        self.logger.info(reply)

    def associate(self,prm):
        base_units = np.pi/180
        units = {'degree': base_units,
                 'arcmin': base_units/60,
                 'arcsec': base_units/60/60,
                 'mas': base_units/60/60/1e3}
        if 'mirror' in prm:
            self.msg['class_id'] = 'GMT'
            self.msg_args['Start'].update(prm)
            if 'state' in prm:
                self.msg_args['Init']['state'] = {prm['mirror']:
                                                  {k:np.asarray(v,dtype=np.double) \
                                                   for k,v in prm['state'].items()}}
                self.msg_args['Start'].pop('state')
            self.msg_args['Update']['mirror'] = prm['mirror']
            self.msg_args['Update']['inputs'].update(\
                    {k_i:v_i.data for k_i,v_i in self.inputs.items()})
        elif 'FEM' in prm:
            self.msg['class_id'] = 'FEM'
            self.msg_args['Start'].update(prm['FEM']['build'])
            self.msg_args['Init'].update({'dt':self.tau,
                                          'inputs':list(self.inputs.keys()),
                                          'outputs':list(self.outputs.keys())})
            self.msg_args['Init'].update(prm['FEM']['reduction'])
            self.msg_args['Update'].update(\
                    {k_i:v_i.data for k_i,v_i in self.inputs.items()})
            self.msg_args['Outputs']['outputs'] += [k_o for k_o in self.outputs]
        elif 'wind loads' in prm:
            self.msg['class_id'] = 'WindLoad'
            self.msg_args['Start'].update(prm['wind loads'])
            self.msg_args['Start'].update({'fs':1/self.tau})
            self.msg_args['Outputs']['outputs'] += [k_o for k_o in self.outputs]
        elif 'edge sensors' in prm:
            self.msg['class_id'] = 'EdgeSensors'
            self.msg_args['Start'].update(prm['edge sensors'])
            self.msg_args['Init'].update(prm['interaction matrices'])
            self.msg_args['Outputs']['outputs'] += [k_o for k_o in self.outputs]
        elif 'source' in prm:
            self.msg['class_id'] = 'OP'
            if isinstance(prm['source']['zenith'],dict):
                prm['source']['zenith'] = np.asarray(prm['source']['zenith']['value'],
                                                     dtype=np.double)*\
                                          units[prm['source']['zenith']['units']]
            if isinstance(prm['source']['azimuth'],dict):
                prm['source']['azimuth'] = np.asarray(prm['source']['azimuth']['value'],
                                                      dtype=np.double)*\
                                          units[prm['source']['azimuth']['units']]
            prm['source'].update({'samplingTime':self.tau*self.sampling_rate})
            self.msg_args['Start'].update({'source_args':prm['source'],
                                           'sensor_class':prm['sensor']['class'],
                                           'sensor_args':{},
                                           'calibration_source_args':None,
                                           'calibrate_args':None})
            if 'source_attributes' in prm:
                src_attr = prm['source_attributes']
                print(src_attr)
                src_attr.update({'timeStamp':self.delay*self.tau})
                if 'rays' in src_attr and \
                   'rot_angle' in  src_attr['rays'] and \
                   isinstance(src_attr['rays']['rot_angle'],dict):
                    src_attr['rays']['rot_angle'] = \
                      np.asarray(src_attr['rays']['rot_angle']['value'])*\
                       units[src_attr['rays']['rot_angle']['units']]
            else:
                src_attr = {'timeStamp':self.delay*self.tau}
            self.msg_args['Start'].update({'source_attributes':src_attr})

            if prm['sensor']['class'] is not None:
                self.msg_args['Start']['sensor_args'].update(prm['sensor']['args'])
                self.msg_args['Start']['calibrate_args'] = prm['sensor']['calibrate_args']
            if 'interaction matrices' in prm:
                self.msg_args['Init'].update(prm['interaction matrices'])
            self.msg_args['Outputs']['outputs'] += [k_o for k_o in self.outputs]
class Client(Driver):
    def __init__(self,tau,tag,logs,delay=0,sampling_rate=1,
                 verbose=logging.INFO,**kwargs):
        Driver.__init__(self,tau,tag)
        self.logger = logging.getLogger(tag)
        self.logger.setLevel(verbose)
        self.delay         = delay
        self.sampling_rate = sampling_rate
        self.inputs       = {}
        try:
            for k in kwargs['inputs']:
                v = kwargs['inputs'][k]
                self.logger.info('New input: %s',k)
                self.inputs[k] = Input(k,**v)
        except KeyError:
            self.logger.info('No inputs!')
        self.outputs       = {}
        try:
            for k in kwargs['outputs']:
                v = kwargs['outputs'][k]
                self.logger.info('New output: %s',k)
                if not 'sampling_rate' in v:
                    v['sampling_rate']=self.sampling_rate
                if v['sampling_rate']<self.sampling_rate:
                    if v['sampling_rate']!=1:
                        self.logger.error('The driver output rate cannot be less than the update rate!')
                    self.logger.warning('Changing the output rate to match the update rate!')
                    v['sampling_rate'] = self.sampling_rate
                if 'logs' in v:
                    logs.add(tag,k,v['logs']['decimation'],self.delay)
                    if v['logs']['decimation']<v['sampling_rate']:
                        if v['logs']['decimation']!=1:
                            self.logger.error('The log decimation rate cannot be less than the output rate!')
                        self.logger.warning('Changing the decimation rate to match the output rate!')
                        v['logs']['decimation'] = v['sampling_rate']
                    v['logs'] = logs.entries[tag][k]
                    self.logger.info('Output logged in!')
                self.outputs[k] = Output(k,**v)
        except KeyError:
            self.logger.info('No inputs!')
        try:
            self.shape = kwargs['shape']
        except KeyError:
            self.shape = None
        try:
            self.split = kwargs['split']
        except KeyError:
            self.split = {'indices_or_sections':1,'axis':0}
        self.system = None

    def start(self):
        self.logger.debug('Starting!')
    def init(self):
        self.logger.debug('Initializing!')
        self.system.init()
    def update(self,step):
        if self.inputs and (step>=self.delay and (step-self.delay)%self.sampling_rate==0):
            self.logger.debug('Updating!')
            u = np.hstack([_.data.reshape(1,-1) for _  in self.inputs.values()])
            self.system.update(u)
            self.logger.debug('u: %s',u.shape)

    def output(self,step):
        if step>=self.delay:
            a = 0
            b = 0
            data = self.system.output().reshape(self.shape)
            self.logger.debug('Output shape: %s', data.shape)
            self.logger.debug('Splitting output: %s',self.split)
            data = np.split( data , **self.split)
            for k,v in self.outputs.items():
                if (step-self.delay)%v.sampling_rate==0:
                    self.logger.debug('Outputing %s [%s]!',k,data[0].shape)
                    v.data[...] = data.pop(0).reshape(v.size)
                    """
                    b = a + v.data.size
                    self.logger.debug('%s [%s]: [%d,%d]',k,v.size,a,b)
                    v.data[...] = self.system.output()[0,a:b].reshape(v.size)
                    a = b
                    """
                    if v.logs is not None and (step-self.delay)%v.logs.decimation==0:
                        self.logger.debug('LOGGING')
                        v.logs.add(v.data.copy())


    def terminate(self):
        self.logger.debug('Terminating!')

    def associate(self,prm):
        sys = list(prm.keys())[0] 
        self.system = getattr(control,sys)(**prm[sys])
class Atmosphere(Driver):
    def __init__(self,tau,tag,server,verbose=logging.INFO,**kwargs):
        Driver.__init__(self,tau,tag)
        self.logger = logging.getLogger(tag)
        self.logger.setLevel(verbose)
        self.server = server
        self.inputs = {}
        self.outputs= {}
        self.msg    = {'class_id':'ATM',
                       'method_id':'Start',
                       'args':{}}
    def start(self):
        self.server._send_(self.msg)
        reply = self.server._recv_()
        self.logger.info('%s',reply)

    def terminate(self):
        self.server._send_({'class_id':'ATM',
                            'method_id':'Terminate',
                            'args':{'args':None}})
        reply = self.server._recv_()
        self.logger.info('%s',reply)

    def associate(self,prm):
        self.msg['args'].update(prm)

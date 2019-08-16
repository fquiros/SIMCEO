import os
import time
import yaml
import logging
import threading
import numpy as np
from . import driver
import zmq
import pickle
import zlib
from graphviz import Digraph

logging.basicConfig()

class Timer(object):
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.tstart = time.time()

    def __exit__(self, type, value, traceback):
        if self.name:
            print('[%s]' % self.name)
        print('Elapsed time: %s' % (time.time() - self.tstart))

class DOS(threading.Thread):
    def __init__(self,path_to_config_dir,verbose=logging.INFO):

        threading.Thread.__init__(self)

        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(verbose)

        cfg_file = os.path.join(path_to_config_dir,'dos.yaml')
        self.logger.info('Reading config from %s',cfg_file)
        with open(cfg_file) as f:
            self.cfg = yaml.load(f)

        self.agent = broker(self.cfg['simulation']['server']['IP'])

        self.N_SAMPLE = int(self.cfg['simulation']['sampling frequency']*
                            self.cfg['simulation']['duration'])
        self.__k_step = 0
        self.pushed = False
        self.initialized = False
        tau = 1/self.cfg['simulation']['sampling frequency']
        self.logs = Logs(tau)
        self.drivers = {}
        for d,v in self.cfg['drivers'].items():
            prm_file = os.path.join(path_to_config_dir,d+'.yaml')
            if os.path.isfile(prm_file):
                self.logger.info('New driver: %s',d)
                if 'server' in v and v['server'] is False:
                    self.drivers[d] = driver.Client(tau,d,
                                                    self.logs,
                                                    verbose=verbose,**v)
                elif d=='atmosphere':
                    self.drivers[d] = driver.Atmosphere(tau,d,self.agent,
                                                        verbose=verbose)
                else:
                    self.drivers[d] = driver.Server(tau,d,
                                                    self.logs,
                                                    self.agent,
                                                    verbose=verbose,**v)
            else:
                self.logger.warning('%s is missing!',prm_file)
        for k_d in self.drivers:
            d = self.drivers[k_d]
            for k_i in d.inputs:
                d.inputs[k_i].tie(self.drivers)
            for k_o in d.outputs:
                d.outputs[k_o].tie(self.drivers)
        for k_d in self.drivers:
            d = self.drivers[k_d]
            device = os.path.join(path_to_config_dir,k_d+'.yaml')
            d.associate(device)
        self.__start = map(lambda x: x.start(), self.drivers.values())
        self.__init = map(lambda x: x.init(), self.drivers.values())
        self.step = self.stepping()
        self.__terminate = map(lambda x: x.terminate(), self.drivers.values())
        self.logger.info('Simulation setup for a duration of {0}s @ {1}Hz ({2} steps)!'.format(
            self.cfg['simulation']['duration'],
            self.cfg['simulation']['sampling frequency'],
            self.N_SAMPLE))

    def push(self):
        self.logger.info('Pushing configuration to server')
        list(self.__start)
        self.pushed = True

    def init(self):
        self.logger.info('Initializing')
        list(self.__init)
        self.initialized = True

    def stepping(self):
        v = self.drivers.values()
        for l in range(self.N_SAMPLE):
            self.logger.debug('Step #%d',l)
            yield [x.update(l) for x in v] + [x.output(l) for x in v]

    def run(self):
        if not self.pushed:
            self.push()
        if not self.initialized:
            self.init()
        self.logger.info('Running')
        with Timer():
            for self.__k_step in range(self.N_SAMPLE):
                next(self.step)
        self.terminate()
    def _run_(self):
        if not self.pushed:
            self.push()
        if not self.initialized:
            self.init()
        self.logger.info('Running')
        with Timer():
            for self.__k_step in range(self.N_SAMPLE):
                next(self.step)
        self.terminate()

    def terminate(self):
        self.logger.info('Terminating')
        list(self.__terminate)

    def diagram(self):
        def add_item(sample_rate,driver_name,method):
            if not sample_rate in sampling:
                sampling[sample_rate] = {}
            if not driver_name in sampling[sample_rate]:
                sampling[sample_rate][driver_name] = [method]
            else:
                sampling[sample_rate][driver_name] += [method]
        def make_nodes(_s_):
            ss = str(_s_)
            c = Digraph(ss)
            c.attr(rank='same')
            c.node(ss,time_label(_s_))
            [c.node(ss+'_'+_,make_label(_,sampling[_s_][_])) for _ in sampling[_s_]]
            return c
        def make_label(d,dv):
            label = "<TR><TD><B>{}</B></TD></TR>".format(d)
            for v in dv:
                label += '''<TR><TD PORT="{0}_{1}">{1}</TD></TR>'''.format(d,v)
            return '''<<TABLE BORDER="0" CELLBORDER="1">{}</TABLE>>'''.format(label)
        def search_method(d,m):
            for s in sampling:
                if d in sampling[s]:
                    if m in sampling[s][d]:
                        return '{0}_{1}:{1}_{2}'.format(str(s),d,m)
        def time_label(n):
            nu = self.cfg['simulation']['sampling frequency']
            t = n/nu
            if t<1:
                return '{:.1f}ms'.format(t*1e3)
            else:
                return '{:.1f}s'.format(t)

        main = Digraph(format='png', node_attr={'shape': 'plaintext'})

        sampling = {}
        for dk in self.drivers:
            d = self.drivers[dk]
            if d.delay>0:
                add_item(d.delay,dk,'delay')
            add_item(d.sampling_rate,dk,'update')
            for ok in d.outputs:
                o = d.outputs[ok]
                add_item(o.sampling_rate,dk,'output')

        s = sorted(sampling)
        [main.subgraph(make_nodes(_)) for _ in s]

        for k in range(1,len(s)):
            main.edge(str(s[k-1]),str(s[k]))

        for s in sampling:
            for d in sampling[s]:
                m = sampling[s][d]
                if not (len(m)==1 and m[0]=='delay'):
                    for ik in self.drivers[d].inputs:
                        data = self.drivers[d].inputs[ik]
                        if data.lien is not None:
                            main.edge(search_method(data.lien[0],'output'),
                                      '{0}_{1}:{1}_update'.format(str(s),d))
                    for ok in self.drivers[d].outputs:
                        data = self.drivers[d].outputs[ok]
                        if data.lien is not None:
                            main.edge('{0}_{1}:{1}_output'.format(str(s),d),
                                      search_method(data.lien[0],'update'))

        return sampling,main

    @property
    def pctComplete(self):
        return round(100*self.__k_step/(self.N_SAMPLE-1))
class Entry:
    def __init__(self,tau,decimation):
        self.tau = tau
        self.decimation = decimation
        self.data = []
    def add(self,value):
        self.data += [value]
    @property
    def timeSeries(self):
        time   = np.arange(len(self.data))*self.decimation*self.tau
        values = np.vstack(self.data) if self.data[0].ndim<2 else np.dstack(self.data)
        return time,values
class Logs:
    def __init__(self,sampling_time):
        self.sampling_time = sampling_time
        self.entries = {}
    def add(self,driver,output,decimation):
        if driver in self.entries:
            self.entries[driver][output] = Entry(self.sampling_time,decimation)
        else:
            self.entries[driver] = {output:Entry(self.sampling_time,decimation)}
    def __repr__(self):
        if self.entries:
            line = ["The 'logs' has {} entries:".format(self.N_entries)]
            for d in self.entries:
                line += [" * {}".format(d)]
                for k,e in enumerate(self.entries[d]):
                    v = self.entries[d][e]
                    if v.data:
                        line += ["   {0}. {1}: {2}x{3}".format(k+1,e,v.data[0].shape,len(v.data))]
                    else:
                        line += ["   {0}. {1}".format(k+1,e)]
        else:
            line = ["The 'logs' has no entries!"]
        return "\n".join(line)
    @property
    def N_entries(self):
        return sum([len(_) for _ in self.entries.values()])
class broker:

    def __init__(self,IP):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.context = zmq.Context()
        self.logger.info("Connecting to server...")
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://{}:3650".format(IP))
        self._send_("Acknowledging connection from SIMCEO client!")
        print(self._recv_())

    def __del__(self):
        self.logger.info('Disconnecting from server!')
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


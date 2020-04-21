import numpy as np
import logging

logging.basicConfig()

class Source:

    def __init__(self,tau,a=5*np.pi/180,max_acc=0.1*np.pi/180):
        self.logger = logging.getLogger(name='Source')
        self.logger.setLevel(logging.INFO)
        self.tau = tau
        self.a = a
        self.max_acc = max_acc
        self.w = np.sqrt(self.max_acc/a)
        self.t = 0.0
        self.t_stop = 2*np.pi/self.w
        self.logger.info("T_stop=%ss",self.t_stop)

    def init(self):
        self.t = -self.tau

    def update(self):
        pass

    def output(self):
        self.t += self.tau
        s = np.zeros(3)
        if self.t<self.t_stop:
            s[0] = self.a*(np.cos(self.w*self.t)-1)
        
        return np.atleast_2d(s)

    def terminate(self):
        pass


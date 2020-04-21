import numpy as np
import scipy.sparse as sparse
import dos.tools as tools
from scipy.linalg import block_diag
import osqp     # OSQP solver
import logging
logging.basicConfig()
import os.path
#import yaml

class SHAcO_qp:
    def __init__(self,D,W2,W3,K,wfsMask,umin,umax,**kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)                        
        
        self.mount_included = False
        if not ((D.shape[1]+2) % 7):
            n_bm = ((D.shape[1]+2)//7) - 12
        elif not ((D.shape[1]+2 -2) % 7):
            n_bm = ((D.shape[1])//7) - 12
            self.mount_included = True
        else:
            self.logger.error('Unable to get the correct number of bending modes. Check Dsh!')

        # W1 can be used to remove mean slopes
        if 'W1' in kwargs.keys():
            self.W1 = kwargs['W1']
        else:
            self.W1 = np.eye(D.shape[0])
        self.DT_W1_D = D.T.dot(self.W1).dot(D)
        self.W1_D = self.W1.dot(D)

        # It is assumed that W3 incorporates the Tu transformation effect
        self.W2, self.W3, self.rho3, self.k = W2, W3, 1e-3, K
        self.wfsMask = wfsMask

        self.umin = umin
        self.umax = umax

        self.n_c_oa = (12+n_bm)*6
        self.DwS7Rz = np.insert(D,[self.n_c_oa+5,self.n_c_oa+10],0,axis=1)

        try:
            self._Tu = kwargs['_Tu']
        except:
            self._Tu = np.eye(D.shape[1])

        if 'J1_J3_ratio' in kwargs.keys():
            self.J1_J3_ratio = kwargs['J1_J3_ratio']
        else:
            self.J1_J3_ratio = 10

        self.__u = np.zeros(0)
        self.logger.debug(' * * * Initializing! * * * ')

        # Reconstructor dimensions
        self.nc = D.shape[1]

        # QP reconstructor matrices
        P = sparse.csc_matrix(self.DT_W1_D+ self.W2+ self.rho3*(self.k**2)*self.W3)
        
        # Inequality constraint matrix: lb <= Ain*u <= ub
        self.Ain = sparse.csc_matrix(   # Remove S7Rz from _Tu
            -np.delete(self._Tu,[self.n_c_oa+5,self.n_c_oa+11], axis=1)*self.k) 
             
        # Create an OSQP object as global
        self.qpp = osqp.OSQP()
        # Setup QP problem
        self.qpp.setup(P=P, q=np.zeros(self.nc), A=self.Ain,
            l=-np.inf*np.ones(self.Ain.shape[0]),u=np.inf*np.ones(self.Ain.shape[0]),
            eps_abs = 1.0e-8, eps_rel = 1.0e-6, max_iter = 500*self.nc,
            verbose=False, warm_start=True)


    def init(self):
        self.__u = np.zeros(self.nc+2) # ! Insert zeros for M1/2S7-Rz
        self.invTu = np.linalg.pinv(self._Tu)


    def update(self,y_sh):
        # AcO state reconstructor
        y_sh = y_sh.ravel()
        y_valid = np.hstack([*[y_sh[MaskSeg.ravel()] for MaskSeg in self.wfsMask]])
        # Remove S7-Rz
        u_ant = np.delete(self.__u,[self.n_c_oa+5,self.n_c_oa+11])
        # Update linear QP term
        q = -y_valid.T.dot(self.W1_D) - self.rho3*u_ant.T.dot(self.W3)*self.k
        
        # Update bounds to inequality constraints
        _Tu_u_ant = self._Tu.dot(self.__u)
        lb = self.umin -_Tu_u_ant
        ub = self.umax -_Tu_u_ant
        # Update QP object and solve problem - 1st step
        self.qpp.update(q=q, l=lb, u=ub)
        X = self.qpp.solve()
        # Check solver status
        if X.info.status == 'solved':
            # Insert zeros for M1/2S7-Rz
            c_hat = np.insert(X.x[:self.nc],[self.n_c_oa+5,self.n_c_oa+10],0)
        else:
            self.logger.info('QP info: %s', X.info.status)
            self.logger.warning('Infeasible QP problem!!!')
            c_hat = np.zeros_like(self.__u)
        
        epsilon = y_valid - self.DwS7Rz.dot(c_hat)
        J1 = epsilon.T.dot(self.W1).dot(epsilon)
        delta = np.delete(self.k*c_hat - self.__u,[self.n_c_oa+5,self.n_c_oa+11])
        J3 = delta.T.dot(self.W3).dot(delta)

        # J3 is zero if delta is also zero -> no need for the 2nd step
        if(J3):
            if(self.rho3):                
                norm_s = np.linalg.norm(y_valid)
                self.logger.info('1st-> J1:%0.3g, J3:%0.3g, ratio:%0.3g, ||s||:%0.3g' %(J1,J3,J1/(self.rho3*J3),norm_s**2))
            else:
                self.logger.info('1st-> J1:%0.3g, J3:%0.3g, ratio:%0.3g, rho3:-X-' %(J1,J3,J1/J3))

            # Update J3 weight
            self.rho3 = max((J1/(self.J1_J3_ratio*J3)),1.0e-6)
            # Update QP object and solve problem - 2nd step
            P = sparse.csc_matrix(self.DT_W1_D+ self.W2+ self.rho3*(self.k**2)*self.W3)
            q = -y_valid.T.dot(self.W1_D) - self.rho3*u_ant.T.dot(self.W3)*self.k
            self.qpp.update(q=q)
            self.qpp.update(Px=sparse.triu(P).data)
            # Solve QP - 2nd Step
            X = self.qpp.solve()
            # Check solver status            
            if X.info.status != 'solved':
                self.logger.warning('QP info: %s', X.info.status)
                self.logger.warning('Infeasible QP problem!!!')
        
            # Insert zeros for M1/2S7-Rz
            c_hat = np.insert(X.x[:self.nc],[self.n_c_oa+5,self.n_c_oa+10],0)

            epsilon = y_valid - self.DwS7Rz.dot(c_hat)
            J1 = epsilon.T.dot(self.W1).dot(epsilon)
            delta = np.delete(self.k*c_hat - self.__u,[self.n_c_oa+5,self.n_c_oa+11])
            J3 = delta.T.dot(self.W3).dot(delta)
            
            self.logger.info('2nd> J1:%0.3g, J3:%0.3g, ratio:%0.3g, rho3:%0.3g' %(J1,J3,J1/(self.rho3*J3),self.rho3))
            

        # Integral controller
        self.__u = self.__u -self.k*c_hat

        # Clip the control signal to the saturation limits [umin,umax] - Should not be necessary if using QP
        if not (empty(self.umin) and empty(self.umax)):
            clip_iter, clip_tol = 0, 1.1
            while (clip_iter<0) and (
                        any(self._Tu.dot(self.__u) > clip_tol*self.umax) or 
                        any(self._Tu.dot(self.__u) < clip_tol*self.umin)):
                clip_iter = clip_iter + 1        
                self.__u = self.invTu.dot(np.clip(self._Tu.dot(self.__u), self.umin, self.umax))
            # Warn clipping iterations required    
            if(clip_iter):
                self.logger.warning('Number of clipping iterations: %d',clip_iter)

        self.logger.debug('u: %s',self.__u)

    def output(self):
        if not self.mount_included:
            return np.atleast_2d(self.__u)
        else:
            self.logger.info('u_mount: %s',self.__u[-2:])
            return np.atleast_2d(self.__u[:-2])

# Function used to test empty constraint vectors
def empty(value):
    try:
        value = np.array(value)
    except ValueError:
        pass
    if value.size:
        return False
    else:
        return True

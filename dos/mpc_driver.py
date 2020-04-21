import numpy as np
import scipy.sparse as sparse
import osqp     # OSQP solver
import logging
logging.basicConfig()
#import yaml

class MPC:
    def __init__(self,A,B,Q,R,npred,dumin,dumax,umin,umax,verbose=logging.INFO,**kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(verbose)
        self.__u = np.zeros(0)
        self.__xpast = np.zeros(0)
        self.xr = np.zeros(0)
        self.npred = npred

#    def init(self,A,B,Q,R,npred,dumin,dumax,umin,umax):
        self.logger.debug('Initializing!')

        # Plant model dimensions
        self.nx = A.shape[0]
        self.nu = B.shape[1]

        # Incremental (augmented) model matrices (Aa,Ba,Ca)
        Aa = np.concatenate((
            np.concatenate((A,np.zeros((self.nx,self.nx))),axis=1),
            np.concatenate((np.eye(self.nx),np.eye(self.nx)),axis=1)),axis=0)
        Ba = np.concatenate((B,np.zeros((self.nx,self.nu))),axis=0)
        Ca = np.concatenate((np.eye(self.nx),np.eye(self.nx)),axis=1)
        # Augmented state dimension
        nxa = Aa.shape[0]

        # MPC model matrices
        # Compute Psi matrix: free response effect on the future outputs
        Phi = np.zeros((self.nx*npred,nxa)) #,Do try Float to speed up?
        for k in range(npred):
            krowInit, krowEnd = k * self.nx, (k+1)*self.nx
            # row indices
            Phi[krowInit:krowEnd, :] = np.dot(Ca,np.linalg.matrix_power(Aa,k+1))

        # Compute Gamma matrix: input effects on future states
        Gamma = np.zeros((self.nx*npred,self.nu*npred))
        # Fill 1st column block of Gamma
        for k in range(npred):
            krowInit, krowEnd = k * self.nx, (k+1)*self.nx
            Gamma[krowInit:krowEnd, 0:self.nu] = np.dot(Ca,np.dot(np.linalg.matrix_power(Aa,k),Ba))
        # Remaining column blocks    
        for k in range(1,npred):
            kGammarowInit, kcolInit, kcolEnd = k*self.nx, k*self.nu, (k+1)*self.nu
            # print(k, '-', kGammarowInit, '-', kcolInit, kcolEnd)
            Gamma[:, kcolInit:kcolEnd] = np.concatenate(
                (np.zeros((kGammarowInit,self.nu)), Gamma[kGammarowInit:,0:self.nu]), axis=0)

        # QP problem quadratic term
        Qkron = sparse.kron(sparse.eye(npred),Q)
        Rkron = sparse.kron(sparse.eye(npred),R)
        P = sparse.csc_matrix((Gamma.T@Qkron@Gamma) + Rkron)

        # Constraint matrices
        Dumin = np.kron(np.ones(npred),dumin)
        Dumax = np.kron(np.ones(npred),dumax)
        Umin = np.kron(np.ones(npred),umin)
        Umax = np.kron(np.ones(npred),umax)

        auxmat = np.zeros((npred,npred))
        for k in range(1,npred+1):
            auxmat[k-1,:k] = np.ones((1,k))

        S = np.kron(auxmat, np.eye(self.nu))
        Ain = sparse.csc_matrix(np.concatenate((np.eye(self.nu*npred),S), axis=0))
        c = np.kron(np.ones((npred,1)), np.eye(self.nu))

        # Create an OSQP object as global
        self.qpp = osqp.OSQP()
        # Setup QP problem
        self.qpp.setup(P, np.zeros(npred*self.nx), Ain,
            np.zeros(Ain.shape[0]), np.zeros(Ain.shape[0]),
            verbose=True, warm_start=True)
        # MPC-QP data matrices
        self.mpc_qpdt = {
            'Phi':Phi, 'GammaT':Gamma.T, 'Qkron':Qkron.toarray(),
            'c':c,'Dumin':Dumin, 'Dumax':Dumax, 'Umin':Umin, 'Umax':Umax
        }

    def init(self):
        self.__u = np.zeros(self.nu)
        self.__xpast = np.zeros(self.nx)
        self.xr = np.zeros(self.nx*self.npred)

    def update(self,x):

        x = x.ravel()
        print("SHAPES: x[{0}], x_past[{1}]".format(x.shape,self.__xpast.shape))
        # State feedback - update MPC internal variables
        xa = np.concatenate((x-self.__xpast,self.__xpast), axis=0)
        self.__xpast = x   # Update past state

        # QP linear term - demands state feedback
        q = np.dot(np.dot(self.mpc_qpdt['GammaT'],self.mpc_qpdt['Qkron']),
                (np.dot(self.mpc_qpdt['Phi'],xa) - self.xr))
        # QP input constraints
        lb = np.concatenate((self.mpc_qpdt['Dumin'],
                self.mpc_qpdt['Umin']-self.mpc_qpdt['c'].dot(self.__u)), axis=0)
        ub = np.concatenate((self.mpc_qpdt['Dumax'],
                self.mpc_qpdt['Umax']-self.mpc_qpdt['c'].dot(self.__u)), axis=0)
        # Update QP variables
        self.qpp.update(q, lb, ub)    
        # Solve QP
        U = self.qpp.solve()
        # Check solver status
        if U.info.status != 'solved':
            self.logger.debug('Infeasible QP problem!!!')
        self.__u = self.__u + U.x[:self.nu]
        self.logger.debug('u: %s',self.__u)

    def output(self):
        return np.atleast_2d(self.__u)

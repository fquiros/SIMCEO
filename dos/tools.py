import pickle
import  numpy as np


def linear_estimator_2_dos(estimator,dos_path, B_or_D='D'):
    """ Convert a linear estimator to a SIMCEO parameter file
    """
    n = estimator.shape[0]
    if B_or_D=='B':
        A = np.zeros((n,n))
        B = estimator
        C = np.eye(n)
        D = np.zeros_like(B)
    if B_or_D=='D':
        A = np.zeros((n,n))
        B = np.zeros_like(estimator)
        C = np.zeros(n)
        D = estimator
    sys = {'System': { 'parameters': {'A':A ,'B':B,'C':C,'D':D} } }
    with open(dos_path+'.pickle', 'wb') as f:
        pickle.dump(sys,f)

def state_space_2_dos(A,B,C,D,dos_path):
    """ Convert a state space model to a SIMCEO parameter file
    """
    sys = {'System': { 'parameters': {'A':A ,'B':B,'C':C,'D':D} } }
    with open(dos_path+'.pickle', 'wb') as f:
        pickle.dump(sys,f)

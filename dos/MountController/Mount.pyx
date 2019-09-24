cdef extern from "Mount.h":
    ctypedef double real_T
    ctypedef struct ExtU_Mount_T:
        real_T Reference[3] #                /* '<Root>/Reference' */
        real_T Feedback[20] #                /* '<Root>/Feedback' */
    ctypedef struct ExtY_Mount_T:
        real_T Output[20] #                  /* '<Root>/Output' */
    ExtU_Mount_T Mount_U
    ExtY_Mount_T Mount_Y
    void Mount_initialize()
    void Mount_step()
    void Mount_terminate()

cimport numpy as np
import numpy as np

class Mount:

    def __init__(self,reference=np.zeros(3)):
        self.reference = reference
        self.__yout = np.zeros(0)

    def init(self):
        Mount_initialize()
        for k in range(3):
            Mount_U.Reference[k] = self.reference[k]
        self.__yout = np.zeros(20)

    def update(self,np.ndarray u):
        #u = np.single(u.ravel())
        cdef double[:] __u
        cdef int k
        __u = np.ravel(np.asarray(u))
        for k in range(20):
            Mount_U.Feedback[k] = __u[k]
        Mount_step()

    def output(self):
        cdef int k
        for k in range(20):
            self.__yout[k] = Mount_Y.Output[k]
        return np.atleast_2d(self.__yout)

    def terminate(self):
        Mount_terminate()


#import pickle
import  numpy as np
import matplotlib.pyplot as plt
#from scipy import sparse
#from scipy.linalg import block_diag

asec2rad = 4.84814e-6
Txyz_scale = 1.0e6 # micro meters
Rxyz_scale = 1.0e3 # m rad

def plot_science(scienceDT, **kwargs):

    if 'k0' in kwargs.keys():
        k0 = kwargs['k0']
    else:
        k0 = 0
    if 'n_w' in kwargs.keys():
        n_w = kwargs['n_w']
    else:
        n_w = scienceDT['wfe_rms'].timeSeries[0].shape[0]
    if 'm1EsDT' in kwargs.keys():
        m1EsDT = kwargs['m1EsDT']
    else:
        m1EsDT = [] 

    wfe_rms = scienceDT['wfe_rms'].timeSeries
    seg_wfe_rms = scienceDT['segment_wfe_rms'].timeSeries
    segpiston = scienceDT['segment_piston'].timeSeries
    tt = scienceDT['tiptilt'].timeSeries
    segtt = scienceDT['segment_tiptilt'].timeSeries
    pssn = scienceDT['PSSn'].timeSeries
    try:
        ESdeltas = m1EsDT['deltas'].timeSeries
    except:
        print('')    

    print('Final values:\n WFE (nm):',wfe_rms[1][-1]*1.0e9,
          '\n', seg_wfe_rms[1][-1,:]*1.0e9,
          '\nPSSn:',pssn[1][-1], 
          '\nsum of abs seg piston (um):',np.sum(np.abs(segpiston[1][-1]))*1.0e6,
          '\n', segpiston[1][-1,:]*1.0e6)

    fig_1 = plt.figure(figsize=(12,6))
    #ax1 = plt.subplot(321)
    ax1 = plt.subplot2grid((3, 2), (0, 0))
    ax1.plot(wfe_rms[0][k0:k0+n_w],wfe_rms[1][k0:k0+n_w]*1.0e9,'x--')
    ax1.grid(True)
    ax1.set_ylabel('WFE RMS (nm)')

    #ax2 = plt.subplot(322)
    ax2 = plt.subplot2grid((3, 2), (0, 1), rowspan=2)
    ax2.plot(wfe_rms[0][k0:k0+n_w],seg_wfe_rms[1][k0:k0+n_w,:]*1.0e9,'x--')
    ax2.grid(True)
    ax2.set_ylabel('Segment WFE RMS (nm)')

    ax3 = plt.subplot2grid((3, 2), (1, 0))
    ax3.plot(pssn[0][k0:k0+n_w],pssn[1][k0:k0+n_w],'x--')
    ax3.grid(True)
    ax3.set_ylabel('PSSn')

    ax4 = plt.subplot2grid((3, 2), (2, 0))
    ax4.plot(segpiston[0][k0:k0+n_w],np.sum(np.abs(segpiston[1]),axis=1)[k0:k0+n_w]*1.0e6,'x--')
    ax4.grid(True)
    ax4.set_ylabel('sum of abs Seg piston (um)')
    ax4.set_xlabel('AcO iteration')

    ax5 = plt.subplot2grid((3, 2), (2, 1))
    ax5.plot(segpiston[0][k0:k0+n_w],segpiston[1][k0:k0+n_w,:]*1.0e6,'x--')
    ax5.grid(True)
    ax5.set_ylabel('Segment piston (um)')
    ax5.set_xlabel('AcO iteration')

    try:
        ESdeltas[0].shape
        plt.figure(figsize=(12,2))
        plt.subplot(221)
        plt.plot(segpiston[0][k0:k0+n_w],np.sum(np.abs(ESdeltas[1]),axis=1)[k0:k0+n_w]*1.0e6,'x--')
        plt.grid(True)
        plt.ylabel('sum of abs ES deltas') 

        plt.subplot(222)
        plt.plot(segpiston[0][k0:k0+n_w],ESdeltas[1][k0:k0+n_w,:],'x--')
        plt.grid(True)
        plt.ylabel('ES deltas')
    except:
        pass

    fig_tt = plt.figure(figsize=(12,2))
    plt.subplot(121)
    plt.plot(tt[0][k0:k0+n_w],tt[1][k0:k0+n_w,:],'x--')
    plt.grid(True)
    plt.ylabel('TT')
    plt.xlabel('AcO iteration')

    plt.subplot(122)
    plt.plot(segtt[0][k0:k0+n_w],segtt[1][k0:k0+n_w,:7],'x--')
    plt.plot(segtt[0][k0:k0+n_w],segtt[1][k0:k0+n_w,7:],'+--')
    plt.grid(True)
    plt.ylabel('Seg TT')
    plt.xlabel('AcO iteration')

    return fig_1, fig_tt


def plot_X0loadComp(m1_x0_dt, m2_x0_dt, controllerDT, show_delta, colors, markers, **kwargs):
    if 'k0' in kwargs.keys():
        k0 = kwargs['k0']
    else:
        k0 = 0 

    M1Txyz, M1Rxyz, M2Txyz, M2Rxyz, M1BM = {}, {}, {}, {}, {}
    M1Txyz_ = controllerDT['M1 Txyz'].timeSeries

    if 'n_w' in kwargs.keys():
        n_w = kwargs['n_w']
    else:
        n_w = controllerDT['M1 Txyz'].timeSeries[0].shape[0] 

    M1Txyz[0] = M1Txyz_[0][k0:k0+n_w]
    M1Txyz[1] = M1Txyz_[1][:,:,k0:k0+n_w]
    M1Rxyz_ = controllerDT['M1 Rxyz'].timeSeries
    M1Rxyz[1] = M1Rxyz_[1][:,:,k0:k0+n_w]
    M2Txyz_ = controllerDT['M2 Txyz'].timeSeries
    M2Txyz[1] = M2Txyz_[1][:,:,k0:k0+n_w]
    M2Rxyz_ = controllerDT['M2 Rxyz'].timeSeries
    M2Rxyz[1] = M2Rxyz_[1][:,:,k0:k0+n_w]
    M1BM_ = controllerDT['M1 BM'].timeSeries
    M1BM[1] = M1BM_[1][:,:,k0:k0+n_w]

    deltaM1Txyz, deltaM1Rxyz = 1.0*np.zeros_like(M1Txyz[1]), 1.0*np.zeros_like(M1Rxyz[1])
    deltaM2Txyz, deltaM2Rxyz = 1.0*np.zeros_like(M2Txyz[1]), 1.0*np.zeros_like(M2Rxyz[1])
    deltaBM = 1.0*np.zeros_like(M1BM[1])

    aux_plt = M1Txyz[0][-1] + 3
    
    fig_rbm = plt.figure(figsize=(12,6))
    plt.subplot(221)
    for kmode in range(3):
        for kseg in range(7):            
            deltaM1Txyz[kseg,kmode,:] = M1Txyz[1][kseg,kmode,:]
            if(show_delta):
                deltaM1Txyz[kseg,kmode,:] = deltaM1Txyz[kseg,kmode,:] + np.array(m1_x0_dt['state']['Txyz'])[kseg,kmode]
            else:
                plt.plot(aux_plt, -np.array(m1_x0_dt['state']['Txyz'])[kseg,kmode]*Txyz_scale,'-',
                    color=colors[kseg], marker=markers[kmode])    
            plt.plot(M1Txyz[0],deltaM1Txyz[kseg,kmode,:]*Txyz_scale,'--', color=colors[kseg], marker=markers[kmode])
    plt.grid(True)
    plt.ylabel('M1 Txyz [um]')
    
    plt.subplot(222)
    for kmode in range(3):
        for kseg in range(7):
            deltaM1Rxyz[kseg,kmode,:] = M1Rxyz[1][kseg,kmode,:]
            if(show_delta):
                deltaM1Rxyz[kseg,kmode,:] = deltaM1Rxyz[kseg,kmode,:] + np.array(m1_x0_dt['state']['Rxyz'])[kseg,kmode]
            else:
                plt.plot(aux_plt, -np.array(m1_x0_dt['state']['Rxyz'])[kseg,kmode]*Rxyz_scale,'-',
                    color=colors[kseg], marker=markers[kmode])
            if(not kseg == 6) or (not kmode == 2):
                plt.plot(M1Txyz[0],deltaM1Rxyz[kseg,kmode,:]*Rxyz_scale,'--', color=colors[kseg], marker=markers[kmode])
    plt.grid(True)
    plt.ylabel('M1 Rxyz [mrad]')

    plt.subplot(223)
    for kmode in range(3):
        for kseg in range(7):
            deltaM2Txyz[kseg,kmode,:] = M2Txyz[1][kseg,kmode,:]
            if(show_delta):
                deltaM2Txyz[kseg,kmode,:] = deltaM2Txyz[kseg,kmode,:] + np.array(m2_x0_dt['state']['Txyz'])[kseg,kmode]
            else:
                plt.plot(aux_plt, -np.array(m2_x0_dt['state']['Txyz'])[kseg,kmode]*Txyz_scale,'-',
                    color=colors[kseg], marker=markers[kmode])    
            plt.plot(M1Txyz[0],deltaM2Txyz[kseg,kmode,:]*Txyz_scale,'--', color=colors[kseg], marker=markers[kmode])
    plt.grid(True)
    plt.ylabel('M2 Txyz [um]')
    plt.xlabel('AcO iteration')

    plt.subplot(224)
    for kmode in range(3):
        for kseg in range(7):
            deltaM2Rxyz[kseg,kmode,:] = M2Rxyz[1][kseg,kmode,:]
            if(show_delta):
                deltaM2Rxyz[kseg,kmode,:] = deltaM2Rxyz[kseg,kmode,:] + np.array(m2_x0_dt['state']['Rxyz'])[kseg,kmode]
            else:
                plt.plot(aux_plt, -np.array(m2_x0_dt['state']['Rxyz'])[kseg,kmode]*Rxyz_scale,'-',
                    color=colors[kseg], marker=markers[kmode])
            if(not kseg == 6) or (not kmode == 2):    
                plt.plot(M1Txyz[0],deltaM2Rxyz[kseg,kmode,:]*Rxyz_scale,'--', color=colors[kseg], marker=markers[kmode])
    plt.grid(True)
    plt.ylabel('M2 Rxyz [mrad]')
    plt.xlabel('AcO iteration')
    plt.show()

    fig_bm = plt.figure(figsize=(12,2))
    for kmode in range(len(M1BM[1][0,:,0])):
        for kseg in range(7):
            deltaBM[kseg,kmode,:] = M1BM[1][kseg,kmode,:]
            if(show_delta):
                deltaBM[kseg,kmode,:] = deltaBM[kseg,kmode,:] + np.array(m1_x0_dt['state']['modes'])[kseg,kmode]
            else:
                plt.plot(aux_plt, -np.array(m1_x0_dt['state']['modes'])[kseg,kmode],'.',
                    color=colors[kseg])    
            plt.plot(deltaBM[kseg,kmode,:],'.--', color=colors[kseg])
    plt.grid(True)
    plt.ylabel('u: M1 BM cmd')
    plt.xlabel('AcO iteration')

    return fig_rbm, fig_bm


def plot_states(X_timeseries, n_bm, colors, markers):

    isample = X_timeseries[0]
    # Indices for M1 states
    indX = np.reshape(np.arange(X_timeseries[1].shape[1]), [7, 6 + 6 + n_bm])
    [i1,i2,i3,i4,i5] = np.split(indX,[3, 6, 9, 12], axis=1)

    xM1_Txyz = X_timeseries[1][:,np.reshape(i1,[7,3])]
    xM1_Rxyz = X_timeseries[1][:,np.reshape(i2,[7,3])]
    xM2_Txyz = X_timeseries[1][:,np.reshape(i3,[7,3])]
    xM2_Rxyz = X_timeseries[1][:,np.reshape(i4,[7,3])]
    xM1_BM = X_timeseries[1][:,np.reshape(i5,[7,n_bm])]
    

    plt.figure(figsize=(16,8))

    plt.subplot(221)
    for kmode in range(3):
        for kseg in range(7):
            plt.plot(isample,xM1_Txyz[:,kseg,kmode]*Txyz_scale,'--', color=colors[kseg], marker=markers[kmode])
    plt.grid(True)
    plt.ylabel('M1 Txyz states [um]')

    plt.subplot(222)
    for kmode in range(3):
        for kseg in range(7):
            plt.plot(isample,xM1_Rxyz[:,kseg,kmode]*Rxyz_scale,'--', color=colors[kseg], marker=markers[kmode])
    plt.grid(True)
    plt.ylabel('M1 Rxyz states [mrad]')    

    plt.subplot(223)
    for kmode in range(3):
        for kseg in range(7):
            plt.plot(isample,xM2_Txyz[:,kseg,kmode]*Txyz_scale,'--', color=colors[kseg], marker=markers[kmode])
    plt.grid(True)
    plt.ylabel('M2 Txyz states [um]')

    plt.subplot(224)
    for kmode in range(3):
        for kseg in range(7):
            plt.plot(isample,xM2_Rxyz[:,kseg,kmode]*Rxyz_scale,'--', color=colors[kseg], marker=markers[kmode])
    plt.grid(True)
    plt.ylabel('M2 Rxyz states [mrad]')   
    plt.show()

    plt.figure(figsize=(16,4))
    for kmode in range(n_bm):
        for kseg in range(7):
            plt.plot(isample,xM1_BM[:,kseg,kmode],'.--', color=colors[kseg])
    plt.grid(True)
    plt.ylabel('M1 BM states')
    plt.show()    


# def plot_m1Forces(controllerDT, show_delta, colors):
#     M1BM = controllerDT['M1 BM'].timeSeries    

#     aux_plt = M1BM[0][-1] + 4
    
#     plt.figure(figsize=(16,4))
#     for kmode in range(len(M1BM[1][0,:,0])):
#         for kseg in range(7):
#             deltaBM[kseg,kmode,:] = M1BM[1][kseg,kmode,:]
#             if(show_delta):
#                 deltaBM[kseg,kmode,:] = deltaBM[kseg,kmode,:] + np.array(m1_x0_dt['state']['modes'])[kseg,kmode]
#             else:
#                 plt.plot(aux_plt, -np.array(m1_x0_dt['state']['modes'])[kseg,kmode],'.',
#                     color=colors[kseg])    
#             plt.plot(deltaBM[kseg,kmode,:],'.--', color=colors[kseg])
#     plt.grid(True)
#     plt.ylabel('u: M1 BM cmd')

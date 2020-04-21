/*
 * File: Mount.h
 *
 * Code generated for Simulink model 'Mount'.
 *
 * Model version                  : 1.8
 * Simulink Coder version         : 8.14 (R2018a) 06-Feb-2018
 * C/C++ source code generated on : Fri Aug 23 11:09:24 2019
 *
 * Target selection: ert.tlc
 * Embedded hardware selection: Intel->x86-64 (Windows64)
 * Code generation objectives: Unspecified
 * Validation result: Not run
 */

#ifndef RTW_HEADER_Mount_h_
#define RTW_HEADER_Mount_h_
#include <string.h>
#include <stddef.h>
#ifndef Mount_COMMON_INCLUDES_
# define Mount_COMMON_INCLUDES_
#include "rtwtypes.h"
#endif                                 /* Mount_COMMON_INCLUDES_ */

#include "Mount_types.h"

/* Macros for accessing real-time model data structure */
#ifndef rtmGetErrorStatus
# define rtmGetErrorStatus(rtm)        ((rtm)->errorStatus)
#endif

#ifndef rtmSetErrorStatus
# define rtmSetErrorStatus(rtm, val)   ((rtm)->errorStatus = (val))
#endif

/* Block states (default storage) for system '<Root>' */
typedef struct {
  real_T Internal_DSTATE[5];           /* '<S6>/Internal' */
  real_T Internal_DSTATE_j[2];         /* '<S57>/Internal' */
  real_T Internal_DSTATE_i[5];         /* '<S3>/Internal' */
  real_T Internal_DSTATE_b[4];         /* '<S2>/Internal' */
  real_T Internal_DSTATE_k[3];         /* '<S20>/Internal' */
  real_T Internal_DSTATE_o[2];         /* '<S17>/Internal' */
  real_T Internal_DSTATE_jx[2];        /* '<S18>/Internal' */
  real_T Internal_DSTATE_h[2];         /* '<S19>/Internal' */
  real_T Internal_DSTATE_n[4];         /* '<S5>/Internal' */
  real_T Internal_DSTATE_hm[3];        /* '<S41>/Internal' */
  real_T Internal_DSTATE_m[2];         /* '<S42>/Internal' */
  real_T Internal_DSTATE_g[2];         /* '<S39>/Internal' */
  real_T Internal_DSTATE_c[2];         /* '<S40>/Internal' */
} DW_Mount_T;

/* Constant parameters (default storage) */
typedef struct {
  /* Pooled Parameter (Expression: [-1 -1 -1 -1 1 1 1 1])
   * Referenced by:
   *   '<S1>/convert to Az drive forces'
   *   '<S1>/convert to El drive forces'
   */
  real_T pooled7[8];
} ConstP_Mount_T;

/* External inputs (root inport signals with default storage) */
typedef struct {
  real_T Reference[3];                 /* '<Root>/Reference' */
  real_T Feedback[20];                 /* '<Root>/Feedback' */
} ExtU_Mount_T;

/* External outputs (root outports fed by signals with default storage) */
typedef struct {
  real_T Output[20];                   /* '<Root>/Output' */
} ExtY_Mount_T;

/* Real-time Model Data Structure */
struct tag_RTM_Mount_T {
  const char_T * volatile errorStatus;
};

/* Block states (default storage) */
extern DW_Mount_T Mount_DW;

/* External inputs (root inport signals with default storage) */
extern ExtU_Mount_T Mount_U;

/* External outputs (root outports fed by signals with default storage) */
extern ExtY_Mount_T Mount_Y;

/* Constant parameters (default storage) */
extern const ConstP_Mount_T Mount_ConstP;

/* Model entry point functions */
extern void Mount_initialize(void);
extern void Mount_step(void);
extern void Mount_terminate(void);

/* Real-time Model object */
extern RT_MODEL_Mount_T *const Mount_M;

/*-
 * The generated code includes comments that allow you to trace directly
 * back to the appropriate location in the model.  The basic format
 * is <system>/block_name, where system is the system number (uniquely
 * assigned by Simulink) and block_name is the name of the block.
 *
 * Note that this particular code originates from a subsystem build,
 * and has its own system numbers different from the parent model.
 * Refer to the system hierarchy for this subsystem below, and use the
 * MATLAB hilite_system command to trace the generated code back
 * to the parent model.  For example,
 *
 * hilite_system('MountCoder/Mount')    - opens subsystem MountCoder/Mount
 * hilite_system('MountCoder/Mount/Kp') - opens and selects block Kp
 *
 * Here is the system hierarchy for this model
 *
 * '<Root>' : 'MountCoder'
 * '<S1>'   : 'MountCoder/Mount'
 * '<S2>'   : 'MountCoder/Mount/Az Encoder Tf'
 * '<S3>'   : 'MountCoder/Mount/Az Motor Tf1'
 * '<S4>'   : 'MountCoder/Mount/Azimuth Controller'
 * '<S5>'   : 'MountCoder/Mount/El Encoder Tf'
 * '<S6>'   : 'MountCoder/Mount/El Motor Tf'
 * '<S7>'   : 'MountCoder/Mount/Elevation Controller'
 * '<S8>'   : 'MountCoder/Mount/GIR Controller'
 * '<S9>'   : 'MountCoder/Mount/GIR Encoder Tf'
 * '<S10>'  : 'MountCoder/Mount/GIR Motor Tf'
 * '<S11>'  : 'MountCoder/Mount/Az Encoder Tf/IO Delay'
 * '<S12>'  : 'MountCoder/Mount/Az Encoder Tf/Input Delay'
 * '<S13>'  : 'MountCoder/Mount/Az Encoder Tf/Output Delay'
 * '<S14>'  : 'MountCoder/Mount/Az Motor Tf1/IO Delay'
 * '<S15>'  : 'MountCoder/Mount/Az Motor Tf1/Input Delay'
 * '<S16>'  : 'MountCoder/Mount/Az Motor Tf1/Output Delay'
 * '<S17>'  : 'MountCoder/Mount/Azimuth Controller/Filter1'
 * '<S18>'  : 'MountCoder/Mount/Azimuth Controller/Filter2'
 * '<S19>'  : 'MountCoder/Mount/Azimuth Controller/Filter3'
 * '<S20>'  : 'MountCoder/Mount/Azimuth Controller/PID+LPF'
 * '<S21>'  : 'MountCoder/Mount/Azimuth Controller/Filter1/IO Delay'
 * '<S22>'  : 'MountCoder/Mount/Azimuth Controller/Filter1/Input Delay'
 * '<S23>'  : 'MountCoder/Mount/Azimuth Controller/Filter1/Output Delay'
 * '<S24>'  : 'MountCoder/Mount/Azimuth Controller/Filter2/IO Delay'
 * '<S25>'  : 'MountCoder/Mount/Azimuth Controller/Filter2/Input Delay'
 * '<S26>'  : 'MountCoder/Mount/Azimuth Controller/Filter2/Output Delay'
 * '<S27>'  : 'MountCoder/Mount/Azimuth Controller/Filter3/IO Delay'
 * '<S28>'  : 'MountCoder/Mount/Azimuth Controller/Filter3/Input Delay'
 * '<S29>'  : 'MountCoder/Mount/Azimuth Controller/Filter3/Output Delay'
 * '<S30>'  : 'MountCoder/Mount/Azimuth Controller/PID+LPF/IO Delay'
 * '<S31>'  : 'MountCoder/Mount/Azimuth Controller/PID+LPF/Input Delay'
 * '<S32>'  : 'MountCoder/Mount/Azimuth Controller/PID+LPF/Output Delay'
 * '<S33>'  : 'MountCoder/Mount/El Encoder Tf/IO Delay'
 * '<S34>'  : 'MountCoder/Mount/El Encoder Tf/Input Delay'
 * '<S35>'  : 'MountCoder/Mount/El Encoder Tf/Output Delay'
 * '<S36>'  : 'MountCoder/Mount/El Motor Tf/IO Delay'
 * '<S37>'  : 'MountCoder/Mount/El Motor Tf/Input Delay'
 * '<S38>'  : 'MountCoder/Mount/El Motor Tf/Output Delay'
 * '<S39>'  : 'MountCoder/Mount/Elevation Controller/Filter2'
 * '<S40>'  : 'MountCoder/Mount/Elevation Controller/Filter3'
 * '<S41>'  : 'MountCoder/Mount/Elevation Controller/PID+LPF1'
 * '<S42>'  : 'MountCoder/Mount/Elevation Controller/filter1'
 * '<S43>'  : 'MountCoder/Mount/Elevation Controller/Filter2/IO Delay'
 * '<S44>'  : 'MountCoder/Mount/Elevation Controller/Filter2/Input Delay'
 * '<S45>'  : 'MountCoder/Mount/Elevation Controller/Filter2/Output Delay'
 * '<S46>'  : 'MountCoder/Mount/Elevation Controller/Filter3/IO Delay'
 * '<S47>'  : 'MountCoder/Mount/Elevation Controller/Filter3/Input Delay'
 * '<S48>'  : 'MountCoder/Mount/Elevation Controller/Filter3/Output Delay'
 * '<S49>'  : 'MountCoder/Mount/Elevation Controller/PID+LPF1/IO Delay'
 * '<S50>'  : 'MountCoder/Mount/Elevation Controller/PID+LPF1/Input Delay'
 * '<S51>'  : 'MountCoder/Mount/Elevation Controller/PID+LPF1/Output Delay'
 * '<S52>'  : 'MountCoder/Mount/Elevation Controller/filter1/IO Delay'
 * '<S53>'  : 'MountCoder/Mount/Elevation Controller/filter1/Input Delay'
 * '<S54>'  : 'MountCoder/Mount/Elevation Controller/filter1/Output Delay'
 * '<S55>'  : 'MountCoder/Mount/GIR Controller/Filter2'
 * '<S56>'  : 'MountCoder/Mount/GIR Controller/Filter3'
 * '<S57>'  : 'MountCoder/Mount/GIR Controller/LTI System14'
 * '<S58>'  : 'MountCoder/Mount/GIR Controller/filter1'
 * '<S59>'  : 'MountCoder/Mount/GIR Controller/Filter2/IO Delay'
 * '<S60>'  : 'MountCoder/Mount/GIR Controller/Filter2/Input Delay'
 * '<S61>'  : 'MountCoder/Mount/GIR Controller/Filter2/Output Delay'
 * '<S62>'  : 'MountCoder/Mount/GIR Controller/Filter3/IO Delay'
 * '<S63>'  : 'MountCoder/Mount/GIR Controller/Filter3/Input Delay'
 * '<S64>'  : 'MountCoder/Mount/GIR Controller/Filter3/Output Delay'
 * '<S65>'  : 'MountCoder/Mount/GIR Controller/LTI System14/IO Delay'
 * '<S66>'  : 'MountCoder/Mount/GIR Controller/LTI System14/Input Delay'
 * '<S67>'  : 'MountCoder/Mount/GIR Controller/LTI System14/Output Delay'
 * '<S68>'  : 'MountCoder/Mount/GIR Controller/filter1/IO Delay'
 * '<S69>'  : 'MountCoder/Mount/GIR Controller/filter1/Input Delay'
 * '<S70>'  : 'MountCoder/Mount/GIR Controller/filter1/Output Delay'
 * '<S71>'  : 'MountCoder/Mount/GIR Encoder Tf/IO Delay'
 * '<S72>'  : 'MountCoder/Mount/GIR Encoder Tf/Input Delay'
 * '<S73>'  : 'MountCoder/Mount/GIR Encoder Tf/Output Delay'
 * '<S74>'  : 'MountCoder/Mount/GIR Motor Tf/IO Delay'
 * '<S75>'  : 'MountCoder/Mount/GIR Motor Tf/Input Delay'
 * '<S76>'  : 'MountCoder/Mount/GIR Motor Tf/Output Delay'
 */
#endif                                 /* RTW_HEADER_Mount_h_ */

/*
 * File trailer for generated code.
 *
 * [EOF]
 */

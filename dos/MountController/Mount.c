/*
 * File: Mount.c
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

#include "Mount.h"
#include "Mount_private.h"

/* Block states (default storage) */
DW_Mount_T Mount_DW;

/* External inputs (root inport signals with default storage) */
ExtU_Mount_T Mount_U;

/* External outputs (root outports fed by signals with default storage) */
ExtY_Mount_T Mount_Y;

/* Real-time model */
RT_MODEL_Mount_T Mount_M_;
RT_MODEL_Mount_T *const Mount_M = &Mount_M_;

/* Model step function */
void Mount_step(void)
{
  /* local block i/o variables */
  real_T rtb_Sum4;
  real_T rtb_Internal;
  real_T rtb_Internal_a;
  real_T rtb_Internal_n;
  real_T rtb_AzAverage;
  real_T rtb_Elaverage;
  real_T rtb_Sum1;
  real_T rtb_Internal_g;
  real_T rtb_Internal_i;
  real_T rtb_Internal_d;
  real_T rtb_Internal_db;
  real_T rtb_Sum;
  real_T rtb_Internal_gr;
  real_T rtb_Internal_k;
  real_T rtb_Internal_o;
  real_T rtb_Internal_nj;
  real_T rtb_Internal_m;
  real_T rtb_Internal_j;
  int32_T i;
  real_T rtb_Sum6_idx_0;
  real_T rtb_Sum6_idx_1;
  real_T rtb_Sum6_idx_2;
  real_T rtb_Sum6_idx_3;

  /* DiscreteStateSpace: '<S6>/Internal' */
  {
    rtb_Internal_m = (0.6282)*Mount_DW.Internal_DSTATE[3] + (-0.2846)*
      Mount_DW.Internal_DSTATE[4];
  }

  /* Gain: '<S1>/average2' incorporates:
   *  Inport: '<Root>/Feedback'
   *  Sum: '<S1>/Sum5'
   */
  rtb_Internal_j = (Mount_U.Feedback[18] - Mount_U.Feedback[16]) * 0.5 +
    (Mount_U.Feedback[19] - Mount_U.Feedback[17]) * 0.5;

  /* Sum: '<S1>/Sum4' incorporates:
   *  Inport: '<Root>/Reference'
   */
  rtb_Sum4 = Mount_U.Reference[2] - rtb_Internal_j;

  /* DiscreteStateSpace: '<S57>/Internal' */
  {
    rtb_Internal = (-734.430524418184)*Mount_DW.Internal_DSTATE_j[0]
      + (159.72299422259294)*Mount_DW.Internal_DSTATE_j[1];
    rtb_Internal += 2.4727E+7*rtb_Sum4;
  }

  /* DiscreteStateSpace: '<S58>/Internal' */
  {
    rtb_Internal_a = 1.0*rtb_Internal;
  }

  /* DiscreteStateSpace: '<S55>/Internal' */
  {
    rtb_Internal_n = 1.0*rtb_Internal_a;
  }

  /* DiscreteStateSpace: '<S56>/Internal' */
  {
    rtb_Internal_j = 1.0*rtb_Internal_n;
  }

  /* Gain: '<S1>/convert to GIR drive forces' */
  rtb_Sum6_idx_0 = -rtb_Internal_j;
  rtb_Sum6_idx_1 = -rtb_Internal_j;
  rtb_Sum6_idx_2 = rtb_Internal_j;
  rtb_Sum6_idx_3 = rtb_Internal_j;

  /* DiscreteStateSpace: '<S3>/Internal' */
  {
    rtb_Internal_j = (0.6282)*Mount_DW.Internal_DSTATE_i[3] + (-0.2846)*
      Mount_DW.Internal_DSTATE_i[4];
  }

  /* Outport: '<Root>/Output' incorporates:
   *  Gain: '<S1>/convert to Az drive forces'
   *  Gain: '<S1>/convert to El drive forces'
   */
  for (i = 0; i < 8; i++) {
    Mount_Y.Output[i] = Mount_ConstP.pooled7[i] * rtb_Internal_j;
    Mount_Y.Output[i + 8] = Mount_ConstP.pooled7[i] * rtb_Internal_m;
  }

  Mount_Y.Output[16] = rtb_Sum6_idx_0;
  Mount_Y.Output[17] = rtb_Sum6_idx_1;
  Mount_Y.Output[18] = rtb_Sum6_idx_2;
  Mount_Y.Output[19] = rtb_Sum6_idx_3;

  /* End of Outport: '<Root>/Output' */

  /* Gain: '<S1>/Az Average' incorporates:
   *  Inport: '<Root>/Feedback'
   *  Sum: '<S1>/Sum7'
   */
  rtb_AzAverage = (((Mount_U.Feedback[4] - Mount_U.Feedback[0]) * 0.25 +
                    (Mount_U.Feedback[5] - Mount_U.Feedback[1]) * 0.25) +
                   (Mount_U.Feedback[6] - Mount_U.Feedback[2]) * 0.25) +
    (Mount_U.Feedback[7] - Mount_U.Feedback[3]) * 0.25;

  /* Gain: '<S1>/El average' incorporates:
   *  Inport: '<Root>/Feedback'
   *  Sum: '<S1>/Sum6'
   */
  rtb_Elaverage = (((Mount_U.Feedback[12] - Mount_U.Feedback[8]) * 0.25 +
                    (Mount_U.Feedback[13] - Mount_U.Feedback[9]) * 0.25) +
                   (Mount_U.Feedback[14] - Mount_U.Feedback[10]) * 0.25) +
    (Mount_U.Feedback[15] - Mount_U.Feedback[11]) * 0.25;

  /* DiscreteStateSpace: '<S2>/Internal' */
  {
    rtb_Internal_j = 0.0*Mount_DW.Internal_DSTATE_b[0] + 0.0*
      Mount_DW.Internal_DSTATE_b[1]
      + 0.0*Mount_DW.Internal_DSTATE_b[2]
      + 1.0*Mount_DW.Internal_DSTATE_b[3];
  }

  /* Sum: '<S1>/Sum1' incorporates:
   *  Inport: '<Root>/Reference'
   */
  rtb_Sum1 = Mount_U.Reference[0] - rtb_Internal_j;

  /* DiscreteStateSpace: '<S20>/Internal' */
  {
    rtb_Internal_g = (1522.6946874633741)*Mount_DW.Internal_DSTATE_k[0]
      + (-1520.1531054342292)*Mount_DW.Internal_DSTATE_k[1]
      + (1517.6162799565832)*Mount_DW.Internal_DSTATE_k[2];
  }

  /* DiscreteStateSpace: '<S17>/Internal' */
  {
    rtb_Internal_i = (-0.091018691539009211)*Mount_DW.Internal_DSTATE_o[0]
      + (0.091018691539009211)*Mount_DW.Internal_DSTATE_o[1];
    rtb_Internal_i += 1.0*rtb_Internal_g;
  }

  /* DiscreteStateSpace: '<S18>/Internal' */
  {
    rtb_Internal_d = (-0.0875714311386453)*Mount_DW.Internal_DSTATE_jx[0]
      + (0.0875714311386453)*Mount_DW.Internal_DSTATE_jx[1];
    rtb_Internal_d += 1.0*rtb_Internal_i;
  }

  /* DiscreteStateSpace: '<S19>/Internal' */
  {
    rtb_Internal_db = (-0.13859619709488769)*Mount_DW.Internal_DSTATE_h[0]
      + (0.13859619709488769)*Mount_DW.Internal_DSTATE_h[1];
    rtb_Internal_db += 1.0*rtb_Internal_d;
  }

  /* DiscreteStateSpace: '<S5>/Internal' */
  {
    rtb_Internal_j = 0.0*Mount_DW.Internal_DSTATE_n[0] + 0.0*
      Mount_DW.Internal_DSTATE_n[1]
      + 0.0*Mount_DW.Internal_DSTATE_n[2]
      + 1.0*Mount_DW.Internal_DSTATE_n[3];
  }

  /* Sum: '<S1>/Sum' incorporates:
   *  Inport: '<Root>/Reference'
   */
  rtb_Sum = Mount_U.Reference[1] - rtb_Internal_j;

  /* DiscreteStateSpace: '<S41>/Internal' */
  {
    rtb_Internal_gr = (1481.6064795149111)*Mount_DW.Internal_DSTATE_hm[0]
      + (-1480.4081991572207)*Mount_DW.Internal_DSTATE_hm[1]
      + (1479.2135384942105)*Mount_DW.Internal_DSTATE_hm[2];
  }

  /* DiscreteStateSpace: '<S42>/Internal' */
  {
    rtb_Internal_k = (-0.0787910027412222)*Mount_DW.Internal_DSTATE_m[0]
      + (0.08352725280526796)*Mount_DW.Internal_DSTATE_m[1];
    rtb_Internal_k += 0.390625*rtb_Internal_gr;
  }

  /* DiscreteStateSpace: '<S39>/Internal' */
  {
    rtb_Internal_o = (-0.089400480737303667)*Mount_DW.Internal_DSTATE_g[0]
      + (0.08842284209960205)*Mount_DW.Internal_DSTATE_g[1];
    rtb_Internal_o += 1.7777777777777777*rtb_Internal_k;
  }

  /* DiscreteStateSpace: '<S40>/Internal' */
  {
    rtb_Internal_nj = (-0.080944953482744)*Mount_DW.Internal_DSTATE_c[0]
      + (0.08018663635532608)*Mount_DW.Internal_DSTATE_c[1];
    rtb_Internal_nj += 1.3108590632220121*rtb_Internal_o;
  }

  /* Update for DiscreteStateSpace: '<S6>/Internal' */
  {
    real_T xnew[5];
    xnew[0] = (0.8282)*Mount_DW.Internal_DSTATE[0];
    xnew[0] += 0.5*rtb_Internal_nj;
    xnew[1] = (1.0)*Mount_DW.Internal_DSTATE[0];
    xnew[2] = (1.0)*Mount_DW.Internal_DSTATE[1];
    xnew[3] = (1.0)*Mount_DW.Internal_DSTATE[2];
    xnew[4] = (1.0)*Mount_DW.Internal_DSTATE[3];
    (void) memcpy(&Mount_DW.Internal_DSTATE[0], xnew,
                  sizeof(real_T)*5);
  }

  /* Update for DiscreteStateSpace: '<S57>/Internal' */
  {
    real_T xnew[2];
    xnew[0] = (0.98399939181919349)*Mount_DW.Internal_DSTATE_j[0]
      + (0.0032188089484772066)*Mount_DW.Internal_DSTATE_j[1];
    xnew[0] += (498.309521784169)*rtb_Sum4;
    xnew[1] = (1.0)*Mount_DW.Internal_DSTATE_j[1];
    xnew[1] += (108.37170599907769)*rtb_Sum4;
    (void) memcpy(&Mount_DW.Internal_DSTATE_j[0], xnew,
                  sizeof(real_T)*2);
  }

  /* Update for DiscreteStateSpace: '<S3>/Internal' */
  {
    real_T xnew[5];
    xnew[0] = (0.8282)*Mount_DW.Internal_DSTATE_i[0];
    xnew[0] += 0.5*rtb_Internal_db;
    xnew[1] = (1.0)*Mount_DW.Internal_DSTATE_i[0];
    xnew[2] = (1.0)*Mount_DW.Internal_DSTATE_i[1];
    xnew[3] = (1.0)*Mount_DW.Internal_DSTATE_i[2];
    xnew[4] = (1.0)*Mount_DW.Internal_DSTATE_i[3];
    (void) memcpy(&Mount_DW.Internal_DSTATE_i[0], xnew,
                  sizeof(real_T)*5);
  }

  /* Update for DiscreteStateSpace: '<S2>/Internal' */
  {
    real_T xtmp = rtb_AzAverage;
    xtmp += (-0.0)*Mount_DW.Internal_DSTATE_b[0] + (-0.0)*
      Mount_DW.Internal_DSTATE_b[1]
      + (-0.0)*Mount_DW.Internal_DSTATE_b[2]
      + (-0.0)*Mount_DW.Internal_DSTATE_b[3];
    Mount_DW.Internal_DSTATE_b[3] = Mount_DW.Internal_DSTATE_b[2];
    Mount_DW.Internal_DSTATE_b[2] = Mount_DW.Internal_DSTATE_b[1];
    Mount_DW.Internal_DSTATE_b[1] = Mount_DW.Internal_DSTATE_b[0];
    Mount_DW.Internal_DSTATE_b[0] = xtmp;
  }

  /* Update for DiscreteStateSpace: '<S20>/Internal' */
  {
    real_T xnew[3];
    xnew[0] = (2.9518004543837795)*Mount_DW.Internal_DSTATE_k[0]
      + (-1.4528848287976501)*Mount_DW.Internal_DSTATE_k[1]
      + (0.95396920321152112)*Mount_DW.Internal_DSTATE_k[2];
    xnew[0] += 8192.0*rtb_Sum1;
    xnew[1] = (2.0)*Mount_DW.Internal_DSTATE_k[0];
    xnew[2] = (0.5)*Mount_DW.Internal_DSTATE_k[1];
    (void) memcpy(&Mount_DW.Internal_DSTATE_k[0], xnew,
                  sizeof(real_T)*3);
  }

  /* Update for DiscreteStateSpace: '<S17>/Internal' */
  {
    real_T xnew[2];
    xnew[0] = (1.9867137427050148)*Mount_DW.Internal_DSTATE_o[0]
      + (-0.98735715064344109)*Mount_DW.Internal_DSTATE_o[1];
    xnew[0] += 0.125*rtb_Internal_g;
    xnew[1] = (1.0)*Mount_DW.Internal_DSTATE_o[0];
    (void) memcpy(&Mount_DW.Internal_DSTATE_o[0], xnew,
                  sizeof(real_T)*2);
  }

  /* Update for DiscreteStateSpace: '<S18>/Internal' */
  {
    real_T xnew[2];
    xnew[0] = (1.9747345342044178)*Mount_DW.Internal_DSTATE_jx[0]
      + (-0.975670759161981)*Mount_DW.Internal_DSTATE_jx[1];
    xnew[0] += 0.25*rtb_Internal_i;
    xnew[1] = (1.0)*Mount_DW.Internal_DSTATE_jx[0];
    (void) memcpy(&Mount_DW.Internal_DSTATE_jx[0], xnew,
                  sizeof(real_T)*2);
  }

  /* Update for DiscreteStateSpace: '<S19>/Internal' */
  {
    real_T xnew[2];
    xnew[0] = (1.9599791155065982)*Mount_DW.Internal_DSTATE_h[0]
      + (-0.96149115980140754)*Mount_DW.Internal_DSTATE_h[1];
    xnew[0] += 0.25*rtb_Internal_d;
    xnew[1] = (1.0)*Mount_DW.Internal_DSTATE_h[0];
    (void) memcpy(&Mount_DW.Internal_DSTATE_h[0], xnew,
                  sizeof(real_T)*2);
  }

  /* Update for DiscreteStateSpace: '<S5>/Internal' */
  {
    real_T xtmp = rtb_Elaverage;
    xtmp += (-0.0)*Mount_DW.Internal_DSTATE_n[0] + (-0.0)*
      Mount_DW.Internal_DSTATE_n[1]
      + (-0.0)*Mount_DW.Internal_DSTATE_n[2]
      + (-0.0)*Mount_DW.Internal_DSTATE_n[3];
    Mount_DW.Internal_DSTATE_n[3] = Mount_DW.Internal_DSTATE_n[2];
    Mount_DW.Internal_DSTATE_n[2] = Mount_DW.Internal_DSTATE_n[1];
    Mount_DW.Internal_DSTATE_n[1] = Mount_DW.Internal_DSTATE_n[0];
    Mount_DW.Internal_DSTATE_n[0] = xtmp;
  }

  /* Update for DiscreteStateSpace: '<S41>/Internal' */
  {
    real_T xnew[3];
    xnew[0] = (2.9518004543837795)*Mount_DW.Internal_DSTATE_hm[0]
      + (-1.4528848287976501)*Mount_DW.Internal_DSTATE_hm[1]
      + (0.95396920321152112)*Mount_DW.Internal_DSTATE_hm[2];
    xnew[0] += 8192.0*rtb_Sum;
    xnew[1] = (2.0)*Mount_DW.Internal_DSTATE_hm[0];
    xnew[2] = (0.5)*Mount_DW.Internal_DSTATE_hm[1];
    (void) memcpy(&Mount_DW.Internal_DSTATE_hm[0], xnew,
                  sizeof(real_T)*3);
  }

  /* Update for DiscreteStateSpace: '<S42>/Internal' */
  {
    real_T xnew[2];
    xnew[0] = (1.9681008878301347)*Mount_DW.Internal_DSTATE_m[0]
      + (-0.96907242630481083)*Mount_DW.Internal_DSTATE_m[1];
    xnew[0] += 0.125*rtb_Internal_gr;
    xnew[1] = (1.0)*Mount_DW.Internal_DSTATE_m[0];
    (void) memcpy(&Mount_DW.Internal_DSTATE_m[0], xnew,
                  sizeof(real_T)*2);
  }

  /* Update for DiscreteStateSpace: '<S39>/Internal' */
  {
    real_T xnew[2];
    xnew[0] = (1.9898401464768214)*Mount_DW.Internal_DSTATE_g[0]
      + (-0.98999726697216606)*Mount_DW.Internal_DSTATE_g[1];
    xnew[0] += 0.125*rtb_Internal_k;
    xnew[1] = (1.0)*Mount_DW.Internal_DSTATE_g[0];
    (void) memcpy(&Mount_DW.Internal_DSTATE_g[0], xnew,
                  sizeof(real_T)*2);
  }

  /* Update for DiscreteStateSpace: '<S40>/Internal' */
  {
    real_T xnew[2];
    xnew[0] = (1.9797310881511048)*Mount_DW.Internal_DSTATE_c[0]
      + (-0.980340944205772)*Mount_DW.Internal_DSTATE_c[1];
    xnew[0] += 0.25*rtb_Internal_o;
    xnew[1] = (1.0)*Mount_DW.Internal_DSTATE_c[0];
    (void) memcpy(&Mount_DW.Internal_DSTATE_c[0], xnew,
                  sizeof(real_T)*2);
  }
}

/* Model initialize function */
void Mount_initialize(void)
{
  /* Registration code */

  /* initialize error status */
  rtmSetErrorStatus(Mount_M, (NULL));

  /* states (dwork) */
  (void) memset((void *)&Mount_DW, 0,
                sizeof(DW_Mount_T));

  /* external inputs */
  (void)memset((void *)&Mount_U, 0, sizeof(ExtU_Mount_T));

  /* external outputs */
  (void) memset(&Mount_Y.Output[0], 0,
                20U*sizeof(real_T));
}

/* Model terminate function */
void Mount_terminate(void)
{
  /* (no terminate code required) */
}

/*
 * File trailer for generated code.
 *
 * [EOF]
 */

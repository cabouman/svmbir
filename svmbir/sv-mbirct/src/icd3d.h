
#ifndef _ICD3D_H_
#define _ICD3D_H_

struct ParamExt
{
    /* QGGMRF derived parameters */
    float pow_sigmaX_p;    /* pow(sigmaX,p) */
    float pow_sigmaX_q;    /* pow(sigmaX,q) */
    float pow_T_qmp;       /* pow(T,q-p) */
    float SigmaXsq;        /* derived parameter: SigmaX^2 */
};

float QGGMRF3D_Update(
	struct ReconParams reconparams,
	struct ParamExt param_ext,
	float tempV,
	float *neighbors,
	float THETA1,
	float THETA2);

float PandP_Update(
	float SigmaXsq,
	float tempV,
	float tempProxMap,
	float THETA1,
	float THETA2);

float QGGMRF_SurrogateCoeff(
	float delta,
	struct ReconParams reconparams,
	struct ParamExt param_ext);

float QGGMRF_Potential(
    float delta,
    struct ReconParams reconparams,
    struct ParamExt param_ext);

void ExtractNeighbors3D(
    float *neighbors,
    int jx,
    int jy,
    float *image,
    struct ImageParams3D imgparams);

#endif

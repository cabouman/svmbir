
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "MBIRModularDefs.h"
#include "MBIRModularUtils.h"
#include "icd3d.h"

	
/* Plug & Play update w/ proximal map prior */
float PandP_Update(float SigmaXsq,float tempV,float tempProxMap,float THETA1,float THETA2)
{
    return(-(SigmaXsq*THETA1 + tempV - tempProxMap) / (SigmaXsq*THETA2 + 1.0));
}

/* ICD update with the QGGMRF prior model */
/* Prior and neighborhood specific */
float QGGMRF3D_Update(struct ReconParams reconparams,struct ParamExt param_ext,float tempV, float *neighbors,float THETA1,float THETA2)
{
    int j; /* Neighbor relative position to Pixel being updated */
    float sum1_Nearest=0, sum1_Diag=0, sum1_Interslice=0; /* for theta1 calculation */
    float sum2_Nearest=0, sum2_Diag=0, sum2_Interslice=0; /* for theta2 calculation */
    float b_nearest, b_diag, b_interslice;
    
    b_nearest=reconparams.b_nearest;
    b_diag=reconparams.b_diag;
    b_interslice = reconparams.b_interslice;

    float delta[10];
    float SurrogateCoeff[10];
    #pragma vector aligned											
    for (j = 0; j < 10; j++)
        delta[j] = tempV - neighbors[j];
    
    for (j = 0; j < 10; j++)
        SurrogateCoeff[j] = QGGMRF_SurrogateCoeff(delta[j],reconparams,param_ext);

    #pragma vector aligned											
    for (j = 0; j < 10; j++)
    {        
        if (j < 4)
        {
            sum1_Nearest += (SurrogateCoeff[j] * delta[j]);
            sum2_Nearest += SurrogateCoeff[j];
        }
        else if (j >= 4 && j<8)
        {
            sum1_Diag += (SurrogateCoeff[j] * delta[j]);
            sum2_Diag += SurrogateCoeff[j];
        }
        else
        {
            sum1_Interslice += (SurrogateCoeff[j] * delta[j]);
            sum2_Interslice += SurrogateCoeff[j];
        }        
        
    }
    
    THETA1 +=  (b_nearest * sum1_Nearest + b_diag * sum1_Diag + b_interslice * sum1_Interslice) ;
    THETA2 +=  (b_nearest * sum2_Nearest + b_diag * sum2_Diag + b_interslice * sum2_Interslice) ;
    return(-THETA1/THETA2);
    
}


/* the potential function of the QGGMRF prior model.  p << q <= 2 */
float QGGMRF_Potential(float delta, struct ReconParams reconparams, struct ParamExt param_ext)
{
    float temp, GGMRF_Pot;
    float p = reconparams.p;
    float q = reconparams.q;
    float T = reconparams.T;
    float SigmaX = reconparams.SigmaX;
    
    GGMRF_Pot = powf(fabs(delta),p)/(p*param_ext.pow_sigmaX_p);
    temp = powf(fabs(delta/(T*SigmaX)), q-p);
    
    return ( GGMRF_Pot * temp/(1.0+temp) );
}

/* Quadratic Surrogate Function for the log(prior model) */
/* For a given convex potential function rho(delta) ... */
/* The surrogate function defined about a point "delta_p", Q(delta ; delta_p), is given by ... */
/* Q(delta ; delta_p) = a(delta_p) * (delta^2/2), where the coefficient a(delta_p) is ... */
/* a(delta_p) = [ rho'(delta_p)/delta_p ]   ... */
/* for the case delta_current is Non-Zero and rho' is the 1st derivative of the potential function */
/* Return this coefficient a(delta_p) */
/* Prior-model specific, independent of neighborhood */

float QGGMRF_SurrogateCoeff(float delta, struct ReconParams reconparams, struct ParamExt param_ext)
{
    float p, q, T, SigmaX, qmp;
    float num, denom, temp;
    float fabs_delta;

    p = reconparams.p;
    q = reconparams.q;
    T = reconparams.T;
    SigmaX = reconparams.SigmaX;
    float pow_sigmaX_p = param_ext.pow_sigmaX_p;
    float pow_sigmaX_q = param_ext.pow_sigmaX_q;
    float pow_T_qmp = param_ext.pow_T_qmp;
    qmp = q - p;
    fabs_delta=(float)fabs(delta);

    /* Refer to MBIP Textbook by C.A. Bouman, */
    /* Table on Quadratic surrogate functions for different prior models */

    if (fabs_delta < 1e-5)
        return 2.0/( p*pow_sigmaX_q*pow_T_qmp ); /* rho"(0) */

    temp = powf(fabs_delta/(T*SigmaX), qmp);
    num = (q/p + temp) * powf(fabs_delta,p-2) * temp;
    denom = pow_sigmaX_p * (1.0+temp) * (1.0+temp);

    return num/denom;
}


void ExtractNeighbors3D(
	float *neighbors,
	int jx,
	int jy,
	float *image,
	struct ImageParams3D imgparams)
{
    int plusx, minusx, plusy, minusy;
    int Nx,Ny;
    //int jz,Nz;
    
    Nx = imgparams.Nx;
    Ny = imgparams.Ny;
    //Nz = imgparams.Nz;
    
    plusx = jx + 1;
    plusx = ((plusx < Nx) ? plusx : 0);
    minusx = jx - 1;
    minusx = ((minusx < 0) ? (Nx-1) : minusx);
    plusy = jy + 1;
    plusy = ((plusy < Ny) ? plusy : 0);
    minusy = jy - 1;
    minusy = ((minusy < 0) ? (Ny-1) : minusy);
    
    neighbors[0] = image[jy*Nx+plusx];
    neighbors[1] = image[jy*Nx+minusx];
    neighbors[2] = image[plusy*Nx+jx];
    neighbors[3] = image[minusy*Nx+jx];

    neighbors[4] = image[plusy*Nx+plusx];
    neighbors[5] = image[plusy*Nx+minusx];
    neighbors[6] = image[minusy*Nx+plusx];
    neighbors[7] = image[minusy*Nx+minusx];
}



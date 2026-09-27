#ifndef MBIR_MODULAR_UTILS_H
#define MBIR_MODULAR_UTILS_H

#include "MBIRModularDefs.h"

/*****************************************************/
/*   Parameter file parsing and printing utilities   */
/*****************************************************/

/* Utility for reading 3D parallel beam sinogram parameters */
/* Returns 0 if no error occurs */
int ReadSinoParams3DParallel(
	char *basename,			/* Source base filename, i.e. <basename>.sinoparams */
	struct SinoParams3DParallel *sinoparams);  /* Sinogram params data structure */

/* Utility for reading 3D image parameters */
/* Returns 0 if no error occurs */
int ReadImageParams3D(
	char *basename,			/* Source base filename, i.e. <basename>.imgparams */
	struct ImageParams3D *imgparams);  /* Image params data structure */

/* Utility for reading reconstruction parameters */
/* Returns 0 if no error occurs */
int ReadReconParams(
	char *basename,			/* Source base filename, i.e. <basename>.reconparams */
	struct ReconParams *reconparams);  /* Reconstruction parameters data structure */

/* Parameter printing utilities */
void printImageParams3D(struct ImageParams3D *imgparams);
void printSinoParams3DParallel(struct SinoParams3DParallel *sinoparams);
void printReconParamsQGGMRF3D(struct ReconParams *reconparams);
void printReconParamsPandP(struct ReconParams *reconparams);


/*******************************/
/*     General purpose I/O     */
/*******************************/

/* General purpose utilities for reading/writing array of floats to/from a file */
/*   Exit codes:                                                      */
/*      0 = success                                                   */
/*      1 = failure: can't open file                                  */
/*      2 = failure: read from (or write to) file terminated early    */
int ReadFloatArray(
	char *fname,	/* source filename */
	float *array,	/* pointer to destination */
	int N);		/* Number of single precision elements to read */

int WriteFloatArray(
	char *fname,	/* destination filename */
	float *array,	/* pointer to source array */
	int N);		/* Number of single precision elements to write */


/**********************************************/
/*     Sinogram I/O and memory allocation     */
/**********************************************/

/* Utilities for reading 3D parallel beam projections and weights */
/* Warning: Memory must be allocated before use */
/* Returns 0 if no error occurs */
int ReadSinoData3DParallel(
	char *basename,		/* Source base filename, i.e. <basename>_slice<Index>.2Dsinodata for given index range */
	struct Sino3DParallel *sinogram);  /* Sinogram data+params data structure */

int ReadWeights3D(
	char *basename,		/* Source base filename, i.e. <basename>_slice<Index>.2Dweightdata for given index range */ 
	struct Sino3DParallel *sinogram);  /* Sinogram data+params data structure */

/* Utilities for writing 3D parallel beam projections and weights */
/* Returns 0 if no error occurs */
int WriteSino3DParallel(
	char *basename,		/* Destination base filename, i.e. <basename>_slice<Index>.2Dsinodata for given index range */
	struct Sino3DParallel *sinogram);  /* Sinogram data+params data structure */

int WriteWeights3D(
	char *basename,		/* Destination base filename, i.e. <basename>_slice<Index>.2Dweightdata for given index range */
	struct Sino3DParallel *sinogram);  /* Sinogram data+params data structure */

/* Utility that allocates memory for both sinogram and weights */
/* Returns 0 if no error occurs */
int AllocateSinoData3DParallel(struct Sino3DParallel *sinogram);

/* Utility for freeing memory allocated for sinogram, weights and ViewAngles */
/* Returns 0 if no error occurs */
int FreeSinoData3DParallel(struct Sino3DParallel *sinogram);


/******************************************/
/*     Image I/O and memory allocation    */
/******************************************/

/* Utility for reading 3D image data */
/* Warning: Memory must be allocated before use */
/* Returns 0 if no error occurs */
int ReadImage3D(
	char *basename,		/* Source base filename, i.e. <basename>_slice<Index>.2Dimgdata for given index range */ 
	struct Image3D *Image);  /* Image data+params data structure */

/* Utility for writing 3D image data */
/* Returns 0 if no error occurs */
int WriteImage3D(
	char *basename,		/* Destination base filename, i.e. <basename>_slice<Index>.2Dimgdata for given index range */ 
	struct Image3D *Image);  /* Image data+params data structure */

/* Utility for allocating memory for a 3D Image */
/* Returns 0 if no error occurs */
int AllocateImageData3D(struct Image3D *Image);

/* Utility for freeing memory a 3D Image */
/* Returns 0 if no error occurs */
int FreeImageData3D(struct Image3D *Image);


/*********************************************************/
/*    Sparse system matrix I/O and memory allocation     */
/*********************************************************/

/* Utility for reading/allocating the Sparse System Matrix */
/* Returns 0 if no error occurs */
/* Warning: Memory is allocated for the data structure inside subroutine */
int ReadSysMatrix2D(
	char *fname,		/* Source base filename, i.e. <fname>.2dsysmatrix */
	struct SysMatrix2D *A);	/* Sparse system matrix structure */

/* Utility for writing the Sparse System Matrix */
/* Returns 0 if no error occurs */
int WriteSysMatrix2D(
	char *fname,		/* Destination base filename, i.e. <fname>.2dsysmatrix */
	struct SysMatrix2D *A);	/* Sparse system matrix structure */

/* Utility for freeing memory from Sparse System Matrix */
/* Returns 0 if no error occurs */
int FreeSysMatrix2D(struct SysMatrix2D *A);



/************************************************************/
/*     Strictly 2D sinogram and image memory allocation     */
/************************************************************/

/* Utility for allocating memory for 2D sinogram and weights */
/* Returns 0 if no error occurs */
int AllocateSinoData2DParallel(
	struct Sino2DParallel *sinogram);  /* 2D Sinogram data+params data structure */

/* Utility for freeing 2D sinogram memory including sino, weights and ViewAngles */
/* Returns 0 if no error occurs */
int FreeSinoData2DParallel(
	struct Sino2DParallel *sinogram);  /* 2D Sinogram data+params data structure */

/* Utility for allocating memory for 2D Image */
/* Returns 0 if no error occurs */
int AllocateImageData2D(
	struct Image2D *Image);  /* 2D Image data+params data structure */

/* Utility for freeing memory for 2D Image */
/* Returns 0 if no error occurs */
int FreeImageData2D(
	struct Image2D *Image);  /* 2D Image data+params data structure */


/************************/
/*    Other utilities   */
/************************/

/* Detect the number of slice index digits in given sinogram data file */
/* Returns number of digits, or 0 if no readable files found */
int NumSinoSliceDigits(char *basename, int slice);

/* Compute sinogram weights */
void ComputeSinoWeights(struct Sino3DParallel sinogram, struct ReconParams reconparams);


#endif /* MBIR_MODULAR_UTILS_H */


#ifndef _ACOMP_H_
#define _ACOMP_H_

#include "MBIRModularDefs.h"

typedef unsigned short channel_t;   // General channel index. Need NChannels < 2^(8*sizeof(channel_t))
typedef unsigned short chanwidth_t; // Channel bandwidth for single pixel, NOT supervoxel
                                    // Note the size of chanwidth_t only affects the internal memory
                                    // when computing A, *not* for the encoded or stored matrix

struct SVParams
{
    struct minStruct *bandMinMap;
    struct maxStruct *bandMaxMap;
    int SVLength;
    int overlap;
    int SVDepth;
    int SV_per_Z;
    int SVsPerRow;
    int Nsv;
    int pieceLength;
};

struct ACol
{
    int n_index;
    chanwidth_t *countTheta;
    channel_t *minIndex;
};

struct AValues_char{
    unsigned char *val;
    channel_t *pieceWiseMin;
    channel_t *pieceWiseWidth;
    int length;
};

struct minStruct
{
    channel_t *bandMin;
};
struct maxStruct
{
    channel_t *bandMax;
};


/* Functions */
void A_comp(
    struct AValues_char **A_Padded_Map,
    float *Aval_max_ptr,
    struct SVParams svpar,
    struct SinoParams3DParallel *sinoparams,
    char *recon_mask,
    struct ImageParams3D *imgparams);

void readAmatrix(
    char *fname,
    struct AValues_char **A_Padded_Map,
    float *Aval_max_ptr,
    struct ImageParams3D *imgparams,
    struct SinoParams3DParallel *sinoparams,
    struct SVParams svpar);

void writeAmatrix(
    char *fname,
    struct AValues_char **A_Padded_Map,
    float *Aval_max_ptr,
    struct ImageParams3D *imgparams,
    struct SinoParams3DParallel *sinoparams,
    struct SVParams svpar);

void AmatrixComputeToFile(
    struct ImageParams3D imgparams,
    struct SinoParams3DParallel sinoparams,
    char *Amatrix_fname,
    char verboseLevel);

#endif

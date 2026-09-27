#ifndef _INITIALIZE_H_
#define _INITIALIZE_H_

#include "A_comp.h"
#include "MBIRModularDefs.h"

void NormalizePriorWeights3D(struct ReconParams *reconparams);
void initSVParams(struct SVParams *svpar,struct ImageParams3D imgparams,struct SinoParams3DParallel sinoparams);
int computePieceLength(int NViews);
char *GenImageReconMask(struct ImageParams3D *imgparams);
void initConstImage(struct Image3D *Image, char *ImageReconMask, float InitValue, float OutsideROIValue);


#endif

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <omp.h>
#ifndef MSVC	/* not included in MS Visual C++ */
    #include <sys/time.h>
#endif

#include "MBIRModularDefs.h"
#include "MBIRModularUtils.h"
#include "allocate.h"
#include "icd3d.h"
#include "heap.h"
#include "A_comp.h"
#include "initialize.h"
#include "recon3d.h"

#define TEST
//#define COMP_COST
//#define COMP_RMSE

/* Internal functions */
void super_voxel_recon(int jj,struct SVParams svpar,unsigned long *NumUpdates,float *totalValue,float *totalChange,int iter,
	char *phaseMap,long *order,int *indexList,float *weight,float *sinoerr,
	struct AValues_char **A_Padded_Map,float *Aval_max_ptr,struct heap_node *headNodeArray,
	struct SinoParams3DParallel sinoparams,struct ReconParams reconparams,struct ParamExt param_ext,float *image,
    struct ImageParams3D imgparams, float *proximalmap, char *group_array,int group_id);
void SVproject(float *proj,float *image,struct AValues_char **A_Padded_Map,float *Aval_max_ptr,
    struct ImageParams3D imgparams,struct SinoParams3DParallel sinoparams,struct SVParams svpar,char backproject_flag);
void coordinateShuffle(int *order1, int *order2,int len);
void three_way_shuffle(long *order1, char *order2, struct heap_node *headNodeArray,int len);
float MAPCostFunction3D(float *x,float *e,float *w,struct ImageParams3D imgparams,struct SinoParams3DParallel sinoparams,
    struct ReconParams reconparams,struct ParamExt param_ext);


void MBIRReconstruct(
    float *image,
    float *sino,
    float *weight,
    float *proj_init,
    float *proximalmap,
    struct ImageParams3D imgparams,
    struct SinoParams3DParallel sinoparams,
    struct ReconParams reconparams,
    char *Amatrix_fname,
    char verboseLevel)
{
    float *sinoerr, *proximalmap_loc=NULL;
    int i,j,jj,p,t,iter,it_print=1;
    size_t k;
    #ifndef MSVC	/* not included in MS Visual C++ */
    struct timeval tm1,tm2;
    #endif

    /* image/sino/recon parameters */
    int Nx = imgparams.Nx;
    int Ny = imgparams.Ny;
    int Nz = imgparams.Nz;
    int Nxy = Nx*Ny;
    int Nvc = sinoparams.NViews * sinoparams.NChannels;
    int MaxIterations = reconparams.MaxIterations;
    float StopThreshold = reconparams.StopThreshold;

    /* Initialize/allocate SV parameters */
    struct AValues_char **A_Padded_Map;
    float *Aval_max_ptr;
    struct SVParams svpar;
    initSVParams(&svpar, imgparams, sinoparams);
    int Nsv = svpar.Nsv;
    int SVLength = svpar.SVLength;
    int SV_per_Z = svpar.SV_per_Z;
    int SVsPerRow = svpar.SVsPerRow;

    /* Activate proximal map mode if given as input */
    if(proximalmap != NULL)
    {
        reconparams.ReconType = MBIR_MODULAR_RECONTYPE_PandP;
        /* 'image' is reconstructed in place, so if proximal map is the same array, make a local copy */
        if(proximalmap == image)
        {
            proximalmap_loc = (float *) mget_spc((size_t)Nx*Ny*Nz,sizeof(float));
            for(k=0; k<(size_t)Nx*Ny*Nz; k++)
                proximalmap_loc[k] = proximalmap[k];
        }
        else
            proximalmap_loc = proximalmap;
    }

    /* print summary to stdout */
    if(verboseLevel>1)
    {
        fprintf(stdout,"MBIRReconstruct() -- build time: %s, %s\n", __DATE__, __TIME__);
        printSinoParams3DParallel(&sinoparams);
        printImageParams3D(&imgparams);
        if(reconparams.ReconType == MBIR_MODULAR_RECONTYPE_QGGMRF_3D)
            printReconParamsQGGMRF3D(&reconparams);
        if(reconparams.ReconType == MBIR_MODULAR_RECONTYPE_PandP)
            printReconParamsPandP(&reconparams);
    }

    /* Allocate and generate recon mask based on ROIRadius */
    char * ImageReconMask = GenImageReconMask(&imgparams);

    /* Read/compute/write System Matrix */
    A_Padded_Map = (struct AValues_char **)multialloc(sizeof(struct AValues_char),2,Nsv,(2*SVLength+1)*(2*SVLength+1));
    Aval_max_ptr = (float *) mget_spc(Nx*Ny,sizeof(float));
    if(Amatrix_fname != NULL)
    {
        if(verboseLevel>1)
            fprintf(stdout,"Reading system matrix...\n");
        readAmatrix(Amatrix_fname, A_Padded_Map, Aval_max_ptr, &imgparams, &sinoparams, svpar);
    }
    else
    {
        if(verboseLevel)
            fprintf(stdout,"Computing system matrix...\n");
        A_comp(A_Padded_Map,Aval_max_ptr,svpar,&sinoparams,ImageReconMask,&imgparams);
    }

    /* Project image for sinogram error */
    if(proj_init != NULL)
        sinoerr = proj_init;
    else
    {
        if(verboseLevel>1)
            fprintf(stdout,"Projecting image...\n");
        sinoerr = (float *) mget_spc((size_t)Nz*Nvc,sizeof(float));
        SVproject(sinoerr,image,A_Padded_Map,Aval_max_ptr,imgparams,sinoparams,svpar,0);
    }
    for(k=0; k<(size_t)Nz*Nvc; k++)
        sinoerr[k] = sino[k]-sinoerr[k];

    /* Recon parameters */
    NormalizePriorWeights3D(&reconparams);
    struct ParamExt param_ext;
    param_ext.pow_sigmaX_p = powf(reconparams.SigmaX,reconparams.p);
    param_ext.pow_sigmaX_q = powf(reconparams.SigmaX,reconparams.q);
    param_ext.pow_T_qmp    = powf(reconparams.T,reconparams.q - reconparams.p);
    param_ext.SigmaXsq = reconparams.SigmaX * reconparams.SigmaX;

    unsigned long NumUpdates=0;
    float totalValue=0,totalChange=0,equits=0;
    float avg_update=0,avg_update_rel=0;
    float c_ratio=0.07;
    float convergence_rho=0.7;
    int rep_num=(int)ceil(1/(4*c_ratio*convergence_rho));
    struct heap priorityheap;
    initialize_heap(&priorityheap);
    long *order;
    char *phaseMap, **group_id_list;

    int NumMaskVoxels=0;
    for(j=0;j<Nxy;j++)
    if(ImageReconMask[j])
        NumMaskVoxels++;

    #ifdef COMP_RMSE
        struct Image3D Image_ref;
        Image_ref.imgparams.Nx = imgparams.Nx;
        Image_ref.imgparams.Ny = imgparams.Ny;
        Image_ref.imgparams.Nz = imgparams.Nz;
        Image_ref.imgparams.FirstSliceNumber = imgparams.FirstSliceNumber;
        Image_ref.imgparams.NumSliceDigits = imgparams.NumSliceDigits;
        AllocateImageData3D(&Image_ref);
        ReadImage3D("ref/ref",&Image_ref);

        float ** image_ref = Image_ref.image;
        double rms_err=0,rms_val=0;
        int jz, Nz0=0, Nz1=Nz;
        for(jz=Nz0; jz<Nz1; jz++)
        for(j=0; j<Nxy; j++)
        if(ImageReconMask[j]) {
            rms_val += image_ref[jz][j]*image_ref[jz][j];
            rms_err += (image[(size_t)jz*Nxy+j]-image_ref[jz][j])*(image[(size_t)jz*Nxy+j]-image_ref[jz][j]);
        }
        rms_val = sqrt(rms_val/((float)NumMaskVoxels*(Nz1-Nz0)));
        rms_err = sqrt(rms_err/((float)NumMaskVoxels*(Nz1-Nz0)));
        FILE *fp_mse=fopen("rmse.txt","w");
        fprintf(fp_mse,"equits|rms_err|rms_val|rms_err/rms_val\n");
        fprintf(fp_mse,"%.2f %g %g %g\n",equits,rms_err,rms_val,rms_err/rms_val);
    #endif

    order = (long *) mget_spc(Nsv*SV_per_Z,sizeof(long));
    phaseMap = (char *) mget_spc(Nsv*SV_per_Z,sizeof(char));
    group_id_list = (char **) multialloc(sizeof(char),2,SV_per_Z,4);

    /* Order of pixel updates need NOT be raster order, just initialize */
    t=0;
    for(p=0;p<Nz;p+=svpar.SVDepth)
    for(i=0;i<Ny;i+=(SVLength*2-svpar.overlap))
    for(j=0;j<Nx;j+=(SVLength*2-svpar.overlap))
    {
        order[t]=(long)p*Nxy+i*Nx+j;  /* order is the first voxel coordinate, not the center */
        t++;
    }

    for(i=0;i<SV_per_Z;i++)
    for(jj=0;jj<Nsv;jj++)
    {
        if((jj/SVsPerRow)%2==0)
        {
            if((jj%SVsPerRow)%2==0)
                phaseMap[i*Nsv+jj]=0;
            else
                phaseMap[i*Nsv+jj]=1;
        }
        else
        {
            if((jj%SVsPerRow)%2==0)
                phaseMap[i*Nsv+jj]=2;
            else
                phaseMap[i*Nsv+jj]=3;
        }
    }

    for(i=0;i<SV_per_Z;i++) {
        if(i%4==0){
            group_id_list[i][0]=0;
            group_id_list[i][1]=3;
            group_id_list[i][2]=1;
            group_id_list[i][3]=2;
        }
        else if(i%4==1) {
            group_id_list[i][0]=3;
            group_id_list[i][1]=0;
            group_id_list[i][2]=2;
            group_id_list[i][3]=1;
        }
        else if(i%4==2) {
            group_id_list[i][0]=1;
            group_id_list[i][1]=2;
            group_id_list[i][2]=3;
            group_id_list[i][3]=0;
        }
        else{
            group_id_list[i][0]=2;
            group_id_list[i][1]=1;
            group_id_list[i][2]=0;
            group_id_list[i][3]=3;
        }
    }
    #ifdef TEST
    srand(0);
    #else
    srand(time(NULL));
    #endif

    struct heap_node *headNodeArray;
    headNodeArray = (struct heap_node *) mget_spc(Nsv*SV_per_Z,sizeof(struct heap_node));

    for(i=0;i<SV_per_Z;i++)
    for(jj=0;jj<Nsv;jj++)
    {
        headNodeArray[i*Nsv+jj].pt=i*Nsv+jj;
        headNodeArray[i*Nsv+jj].x=0.0;
    }
    //int indexList_size=(int) Nsv*SV_per_Z*4*c_ratio*(1-convergence_rho);
    int indexList_size= Nsv*SV_per_Z/4;
    int * indexList = (int *) mget_spc(indexList_size,sizeof(int));

    //coordinateShuffle(&order[0],&phaseMap[0],Nsv*SV_per_Z);
    long tmp_long;
    char tmp_char;
    for(i=0; i<Nsv*SV_per_Z-1; i++)
    {
        j = i + (rand() % (Nsv*SV_per_Z-i));
        tmp_long = order[j];
        order[j] = order[i];
        order[i] = tmp_long;
        tmp_char = phaseMap[j];
        phaseMap[j] = phaseMap[i];
        phaseMap[i] = tmp_char;
    }

    iter=0;
    char stop_FLAG=0;
    int startIndex=0;
    int endIndex=0;

    if(verboseLevel) {
        fprintf(stdout,"Reconstructing...\n");
        #ifndef MSVC	/* not included in MS Visual C++ */
        gettimeofday(&tm1,NULL);
        #endif
    }

    // Limit threads for smaller problem size
    // Want on average 1 thread per SV row/col within each slice block
    // The /2 is on account of the phased checkerboard grouping
    int max_threads = omp_get_max_threads();
    i = ((Nx < Ny) ? Nx : Ny) / (2*SVLength-svpar.overlap) / 2 * SV_per_Z;
    max_threads = ( i < max_threads) ? i : max_threads;

    #pragma omp parallel num_threads(max_threads)
    {
        while(stop_FLAG==0 && equits<MaxIterations && iter<100*MaxIterations)
        {
            #pragma omp single
            {
                if(iter==0)
                {
                    startIndex=0;
                    endIndex=Nsv*SV_per_Z;
                }
                else
                {
                    if((iter-1)%(2*rep_num)==0 && iter!=1)
                        three_way_shuffle(&order[0],&phaseMap[0],&headNodeArray[0],Nsv*SV_per_Z);

                    if(iter%2==1)
                    {
                        priorityheap.size=0;
                        for(jj=0;jj<Nsv*SV_per_Z;jj++){
                            heap_insert(&priorityheap, &(headNodeArray[jj]));
                        }
                        startIndex=0;
                        endIndex=indexList_size;

                        for(i=0;i<endIndex;i++) {
                            struct heap_node tempNode;
                            get_heap_max(&priorityheap, &tempNode);
                            indexList[i]=tempNode.pt;
                        }
                    }
                    else {
                        startIndex=((iter-2)/2)%rep_num*Nsv*SV_per_Z/rep_num;
                        endIndex=(((iter-2)/2)%rep_num+1)*Nsv*SV_per_Z/rep_num;
                    }
                }
            }

            int group=0;

            for (group = 0; group < 4; group++)
            {
                if(iter%2 == 1 && reconparams.Positivity==0)
                {   // Non-homogeneous update + no positivity constraint
                    // SJK: using static scheduling for non-homogeneous case because
                    // structural features can cause spatial alignment among SVs at
                    // the top of the priority queue. Dynamic scheduling will tend to
                    // schedule these at the same time--bad because of potential instability
                    // in the case positivity constraint is turned off
                    #pragma omp for schedule(static) reduction(+:NumUpdates) reduction(+:totalValue) reduction(+:totalChange)
                    for (jj = startIndex; jj < endIndex; jj+=1)
                        super_voxel_recon(jj,svpar,&NumUpdates,&totalValue,&totalChange,iter,
                                &phaseMap[0],order,&indexList[0],weight,sinoerr,A_Padded_Map,&Aval_max_ptr[0],
                                &headNodeArray[0],sinoparams,reconparams,param_ext,image,imgparams,proximalmap_loc,
                                &group_id_list[0][0],group);
                }
                else  // iter%2==0 Homogeneous update
                {
                    #pragma omp for schedule(dynamic) reduction(+:NumUpdates) reduction(+:totalValue) reduction(+:totalChange)
                    for (jj = startIndex; jj < endIndex; jj+=1)
                        super_voxel_recon(jj,svpar,&NumUpdates,&totalValue,&totalChange,iter,
                                &phaseMap[0],order,&indexList[0],weight,sinoerr,A_Padded_Map,&Aval_max_ptr[0],
                                &headNodeArray[0],sinoparams,reconparams,param_ext,image,imgparams,proximalmap_loc,
                                &group_id_list[0][0],group);
                }
            }

            #pragma omp single
            {
                avg_update=avg_update_rel=0.0;
                if(NumUpdates>0) {
                    avg_update = totalChange/NumUpdates;
                    float avg_value = totalValue/NumUpdates;
                    if(avg_value > 0.0)
                        avg_update_rel = avg_update/avg_value * 100;
                    else
                        avg_update_rel = avg_update;
                    //printf("avg_update %f, avg_value %f, avg_update_rel %f\n",avg_update,avg_value,avg_update_rel);
                }
                #ifdef COMP_COST
                float cost = MAPCostFunction3D(image,sinoerr,weight,imgparams,sinoparams,reconparams,param_ext);
                fprintf(stdout, "it %d cost = %-15f, avg_update %f \n", iter, cost, avg_update);
                #endif

                if (avg_update_rel < StopThreshold && (endIndex!=0))
                    stop_FLAG = 1;

                iter++;
                equits += (float)NumUpdates/((float)NumMaskVoxels*Nz);

                if(verboseLevel && equits > it_print) {
                    fprintf(stdout,"\titeration %d, average change %.4f %%\n",it_print,avg_update_rel);
                    it_print++;
                }

                #ifdef COMP_RMSE
                    rms_err=0;
                    for(jz=Nz0; jz<Nz1; jz++)
                    for(j=0; j<Nxy; j++)
                    if(ImageReconMask[j])
                        rms_err += (image[(size_t)jz*Nxy+j]-image_ref[jz][j])*(image[(size_t)jz*Nxy+j]-image_ref[jz][j]);
                    rms_err = sqrt(rms_err/((float)NumMaskVoxels*(Nz1-Nz0)));
                    fprintf(fp_mse,"%.2f %g %g %g\n",equits,rms_err,rms_val,rms_err/rms_val);
                #endif

                NumUpdates=0;
                totalValue=0;
                totalChange=0;
            }
        }
    }

    if(verboseLevel)
    {
        if(StopThreshold <= 0)
            fprintf(stdout,"\tNo stopping condition--running fixed iterations\n");
        else if(stop_FLAG == 1)
            fprintf(stdout,"\tReached stopping condition\n");
        else
            fprintf(stdout,"\tWarning: Didn't reach stopping condition\n");
        if(verboseLevel>1)
        {
            fprintf(stdout,"\tEquivalent iterations = %.1f, (non-homogeneous iterations = %d)\n",equits,iter);
            fprintf(stdout,"\tAverage update in last iteration (relative) = %f %%\n",avg_update_rel);
            fprintf(stdout,"\tAverage update in last iteration (magnitude) = %.4g\n",avg_update);
        }
        #ifndef MSVC	/* not included in MS Visual C++ */
        gettimeofday(&tm2,NULL);
        unsigned long long tt = 1000 * (tm2.tv_sec - tm1.tv_sec) + (tm2.tv_usec - tm1.tv_usec) / 1000;
        printf("\tReconstruction time = %llu ms (iterations only)\n", tt);
        #endif
    }

    /* If initial projection was supplied, update to return final projection */
    if(proj_init != NULL)
    {
        for(k=0; k<(size_t)Nz*Nvc; k++)
            proj_init[k] = sino[k]-sinoerr[k];
    }
    else
        free((void *)sinoerr);

    /* If local copy of proximal map was made, free it */
    if(proximalmap == image)
        free((void *)proximalmap_loc);

    free((void *)headNodeArray);
    free_heap((void *)&priorityheap);
    free((void *)order);
    free((void *)phaseMap);
    multifree(group_id_list,2);
    free((void *)indexList);

    #ifdef COMP_RMSE
        FreeImageData3D(&Image_ref);
        fclose(fp_mse);
    #endif

    /* Free SV memory */
    for(i=0;i<Nsv;i++) {
        free((void *)svpar.bandMinMap[i].bandMin);
        free((void *)svpar.bandMaxMap[i].bandMax);
    }
    free((void *)svpar.bandMinMap);
    free((void *)svpar.bandMaxMap);

    /* Free system matrix */
    for(i=0;i<Nsv;i++)
    for(j=0;j<(2*SVLength+1)*(2*SVLength+1);j++)
    if(A_Padded_Map[i][j].length>0)
    {
        free((void *)A_Padded_Map[i][j].val);
        free((void *)A_Padded_Map[i][j].pieceWiseMin);
        free((void *)A_Padded_Map[i][j].pieceWiseWidth);
    }
    multifree(A_Padded_Map,2);
    free((void *)Aval_max_ptr);
    free((void *)ImageReconMask);

}   /*  END MBIRReconstruct()  */

				
void super_voxel_recon(
    int jj,
    struct SVParams svpar,
    unsigned long *NumUpdates,
    float *totalValue,
    float *totalChange,
    int iter,
    char *phaseMap,
    long *order,
    int *indexList,
    float *weight,
    float *sinoerr,
    struct AValues_char ** A_Padded_Map,
    float *Aval_max_ptr,
    struct heap_node *headNodeArray,
    struct SinoParams3DParallel sinoparams,
    struct ReconParams reconparams,
    struct ParamExt param_ext,
    float *image,
    struct ImageParams3D imgparams,
    float *proximalmap,
    char *group_array,
    int group_id)
{
    int p,i,q,t,j,currentSlice;
    float *tempProxMap=NULL;
    int NumUpdates_loc=0;
    float totalValue_loc=0,totalChange_loc=0;

    int Nx = imgparams.Nx;
    int Ny = imgparams.Ny;
    int Nz = imgparams.Nz;
    int Nxy = Nx*Ny;
    int Nvc = sinoparams.NViews * sinoparams.NChannels;
    char PositivityFlag = reconparams.Positivity;

    int SV_depth_modified, SVPosition;
    int SVLength = svpar.SVLength;
    int overlappingDistance = svpar.overlap;
    int SV_depth = svpar.SVDepth;
    int SVsPerRow = svpar.SVsPerRow;
    struct minStruct * bandMinMap = svpar.bandMinMap;
    struct maxStruct * bandMaxMap = svpar.bandMaxMap;
    int pieceLength = svpar.pieceLength;
    int NViewSets = sinoparams.NViews/pieceLength;

    int jj_new;
    if(iter%2==0)
        jj_new=jj;
    else
        jj_new=indexList[jj];

    int startSlice = order[jj_new] / Nxy;

    if(phaseMap[jj_new] != group_array[startSlice/SV_depth*4+group_id])
        return;

    int jy = (order[jj_new] - startSlice*Nxy) / Nx;
    int jx = (order[jj_new] - startSlice*Nxy) % Nx;

    if((startSlice+SV_depth)>Nz)
        SV_depth_modified=Nz-startSlice;
    else
        SV_depth_modified=SV_depth;

    SVPosition = jy/(2*SVLength-overlappingDistance)*SVsPerRow+jx/(2*SVLength-overlappingDistance);

    int countNumber=0;	/* number of voxels in given SV */
    int coordinateSize=(2*SVLength+1)*(2*SVLength+1);
    int * k_newCoordinate = (int *) mget_spc(coordinateSize,sizeof(int));
    int * j_newCoordinate = (int *) mget_spc(coordinateSize,sizeof(int));
    int j_newAA,k_newAA;
    int voxelIncrement=0;

    /* choosing the voxels locations in an SV */
    for(j_newAA=jy;j_newAA<=(jy+2*SVLength);j_newAA++)
    for(k_newAA=jx;k_newAA<=(jx+2*SVLength);k_newAA++) {
        if(j_newAA>=0 && k_newAA >=0 && j_newAA <Ny && k_newAA < Nx) {
            if(A_Padded_Map[SVPosition][voxelIncrement].length >0) {
                j_newCoordinate[countNumber]=j_newAA;
                k_newCoordinate[countNumber]=k_newAA;
                countNumber++;
            }
        }
        voxelIncrement++;
    }

    /* if no voxels in this region skip this loop iteration */
    if(countNumber==0)
    {
        free((void *)k_newCoordinate);
        free((void *)j_newCoordinate);
        return;
    }

    coordinateShuffle(&j_newCoordinate[0],&k_newCoordinate[0],countNumber);

    /*XW: for a supervoxel, bandMin records the starting position of the sinogram band at each view*/
    /*XW: for a supervoxel, bandMax records the end position of the sinogram band at each view */
    channel_t * bandMin = (channel_t *) mget_spc(sinoparams.NViews,sizeof(channel_t));
    channel_t * bandMax = (channel_t *) mget_spc(sinoparams.NViews,sizeof(channel_t));
    channel_t * bandWidthTemp = (channel_t *) mget_spc(sinoparams.NViews,sizeof(channel_t));
    channel_t * bandWidth = (channel_t *) mget_spc(NViewSets,sizeof(channel_t));

    memcpy(&bandMin[0],&bandMinMap[SVPosition].bandMin[0],sizeof(channel_t)*(sinoparams.NViews));
    memcpy(&bandMax[0],&bandMaxMap[SVPosition].bandMax[0],sizeof(channel_t)*(sinoparams.NViews));

    //#pragma vector aligned
    for(p=0;p< sinoparams.NViews;p++)
        bandWidthTemp[p]=bandMax[p]-bandMin[p];

    for (p = 0; p < NViewSets; p++)
    {
        int bandWidthMax=bandWidthTemp[p*pieceLength];
        for(t=0;t<pieceLength;t++){
            if(bandWidthTemp[p*pieceLength+t]>bandWidthMax)
                bandWidthMax=bandWidthTemp[p*pieceLength+t];
        }
        bandWidth[p]=bandWidthMax;
    }

    float ** newWArray = (float **)malloc(sizeof(float *) * NViewSets);
    float ** newEArray = (float **)malloc(sizeof(float *) * NViewSets);
    float ** CopyNewEArray = (float **)malloc(sizeof(float *) * NViewSets);

    for (p = 0; p < NViewSets; p++) {
        newWArray[p] = (float *)malloc(sizeof(float)*bandWidth[p]*pieceLength*SV_depth_modified);
        newEArray[p] = (float *)malloc(sizeof(float)*bandWidth[p]*pieceLength*SV_depth_modified);
        CopyNewEArray[p] = (float *)malloc(sizeof(float)*bandWidth[p]*pieceLength*SV_depth_modified);
    }

    float *newWArrayPointer;
    float *newEArrayPointer;
    float **newWArrayTransposed;
    float **newEArrayTransposed;
    float *WTransposeArrayPointer;
    float *ETransposeArrayPointer;

    /*XW: copy the interlaced we into the memory buffer*/
    for (p = 0; p < NViewSets; p++)
    {
        newWArrayPointer=&newWArray[p][0];
        newEArrayPointer=&newEArray[p][0];
        for(i=0;i<SV_depth_modified;i++)
        for(q=0;q<pieceLength;q++)
        {
            memcpy(newWArrayPointer,&weight[(size_t)(startSlice+i)*Nvc+p*pieceLength*sinoparams.NChannels+q*sinoparams.NChannels+bandMin[p*pieceLength+q]],sizeof(float)*(bandWidth[p]));
            memcpy(newEArrayPointer,&sinoerr[(size_t)(startSlice+i)*Nvc+p*pieceLength*sinoparams.NChannels+q*sinoparams.NChannels+bandMin[p*pieceLength+q]],sizeof(float)*(bandWidth[p]));
            newWArrayPointer+=bandWidth[p];
            newEArrayPointer+=bandWidth[p];
        }
    }

    for (p = 0; p < NViewSets; p++)
        memcpy(&CopyNewEArray[p][0],&newEArray[p][0],sizeof(float)*bandWidth[p]*pieceLength*SV_depth_modified);

    newWArrayTransposed = (float **)malloc(sizeof(float *) * NViewSets);
    newEArrayTransposed = (float **)malloc(sizeof(float *) * NViewSets);

    for (p = 0; p < NViewSets; p++)
    {
        newWArrayTransposed[p] = (float *)malloc(sizeof(float)*bandWidth[p]*pieceLength*SV_depth_modified);
        newEArrayTransposed[p] = (float *)malloc(sizeof(float)*bandWidth[p]*pieceLength*SV_depth_modified);
    }

    for (p = 0; p < NViewSets; p++)
    for(currentSlice=0;currentSlice<(SV_depth_modified);currentSlice++) 
    {
        WTransposeArrayPointer=&newWArrayTransposed[p][currentSlice*bandWidth[p]*pieceLength];
        ETransposeArrayPointer=&newEArrayTransposed[p][currentSlice*bandWidth[p]*pieceLength];
        newEArrayPointer=&newEArray[p][currentSlice*bandWidth[p]*pieceLength];
        newWArrayPointer=&newWArray[p][currentSlice*bandWidth[p]*pieceLength];
        for(q=0;q<bandWidth[p];q++)
        {
            #pragma vector aligned
            for(t=0;t<pieceLength;t++)
            {
                ETransposeArrayPointer[q*pieceLength+t]=newEArrayPointer[bandWidth[p]*t+q];
                WTransposeArrayPointer[q*pieceLength+t]=newWArrayPointer[bandWidth[p]*t+q];
            }
        }
    }

    WTransposeArrayPointer=&newWArrayTransposed[0][0];
    ETransposeArrayPointer=&newEArrayTransposed[0][0];
    newEArrayPointer=&newEArray[0][0];

    for (p = 0; p < NViewSets; p++)
        free((void *)newWArray[p]);
    free((void **)newWArray);

    /* Turn off zero-skipping for 1st iteration */
    char zero_skip_enable=0;  // 1: enable, 0: disable
    if(iter>0 && PositivityFlag)
        zero_skip_enable=1;

    /*XW: the start of the loop to compute theta1, theta2*/
    float * THETA1 = (float *) get_spc(SV_depth_modified,sizeof(float));
    float * THETA2 = (float *) get_spc(SV_depth_modified,sizeof(float));
    float * tempV = (float *) mget_spc(SV_depth_modified,sizeof(float));
    float * diff = (float *) mget_spc(SV_depth_modified,sizeof(float));
    float ** neighbors = (float **) multialloc(sizeof(float),2,SV_depth_modified,10);
    char * zero_skip_FLAG = (char *) mget_spc(SV_depth_modified,sizeof(char));
    if(reconparams.ReconType == MBIR_MODULAR_RECONTYPE_PandP)
        tempProxMap = (float *) mget_spc(SV_depth_modified,sizeof(float));

    for(i=0;i<countNumber;i++)
    {
        const short j_new = j_newCoordinate[i];   /*XW: get the voxel's x,y location*/
        const short k_new = k_newCoordinate[i];
        float Aval_max = Aval_max_ptr[j_new*Nx+k_new];

        for(p=0;p<SV_depth_modified;p++)
            THETA1[p]=THETA2[p]=0.0;

        int theVoxelPosition=(j_new-jy)*(2*SVLength+1)+(k_new-jx);
        unsigned char * A_padd_Tranpose_pointer = &A_Padded_Map[SVPosition][theVoxelPosition].val[0];

        for(currentSlice=0;currentSlice<SV_depth_modified;currentSlice++)
        {
            tempV[currentSlice] = (float)(image[(size_t)(startSlice+currentSlice)*Nxy + j_new*Nx+k_new]); /* current voxel value */

            zero_skip_FLAG[currentSlice] = 0;

            if(reconparams.ReconType == MBIR_MODULAR_RECONTYPE_QGGMRF_3D)
            {
                ExtractNeighbors3D(&neighbors[currentSlice][0],k_new,j_new,&image[(size_t)(startSlice+currentSlice)*Nxy],imgparams);

                if((startSlice+currentSlice)==0)
                    neighbors[currentSlice][8]=0.0;
                else
                    neighbors[currentSlice][8]=image[(size_t)(startSlice+currentSlice-1)*Nxy + j_new*Nx+k_new];

                if((startSlice+currentSlice)<(Nz-1))
                    neighbors[currentSlice][9]=image[(size_t)(startSlice+currentSlice+1)*Nxy + j_new*Nx+k_new];
                else
                    neighbors[currentSlice][9]=0.0;

                if(zero_skip_enable)
                if(tempV[currentSlice] == 0.0)
                {
                    zero_skip_FLAG[currentSlice] = 1;
                    for (j = 0; j < 10; j++)
                    {
                        if (neighbors[currentSlice][j] != 0.0)
                        {
                            zero_skip_FLAG[currentSlice] = 0;
                            break;
                        }
                    }
                }
            }
            if(reconparams.ReconType == MBIR_MODULAR_RECONTYPE_PandP)
                tempProxMap[currentSlice] = proximalmap[(startSlice+currentSlice)*Nxy + j_new*Nx+k_new];
        }

        A_padd_Tranpose_pointer = &A_Padded_Map[SVPosition][theVoxelPosition].val[0];

        for(p=0;p<NViewSets;p++)
        {
            int myCount=A_Padded_Map[SVPosition][theVoxelPosition].pieceWiseWidth[p];
            int pieceMin=A_Padded_Map[SVPosition][theVoxelPosition].pieceWiseMin[p];
            #pragma vector aligned
            for(currentSlice=0;currentSlice<SV_depth_modified;currentSlice++)
            if(zero_skip_FLAG[currentSlice] == 0)
            {
                WTransposeArrayPointer=&newWArrayTransposed[p][currentSlice*bandWidth[p]*pieceLength];
                ETransposeArrayPointer=&newEArrayTransposed[p][currentSlice*bandWidth[p]*pieceLength];
                WTransposeArrayPointer+=pieceMin*pieceLength;
                ETransposeArrayPointer+=pieceMin*pieceLength;
                float tempTHETA1=0.0;
                float tempTHETA2=0.0;
                //Not finding evidence this makes a difference --SJK
                //Deprecated by Intel anyway
                //#pragma vector aligned
                //#pragma simd reduction(+:tempTHETA2,tempTHETA1)
                for(t=0;t<myCount*pieceLength;t++)
                {	/* summing over voxels which are not skipped or masked*/
                    tempTHETA1 += A_padd_Tranpose_pointer[t]*WTransposeArrayPointer[t]*ETransposeArrayPointer[t];
                    tempTHETA2 += A_padd_Tranpose_pointer[t]*WTransposeArrayPointer[t]*A_padd_Tranpose_pointer[t];
                }
                THETA1[currentSlice]+=tempTHETA1;
                THETA2[currentSlice]+=tempTHETA2;
            }
            A_padd_Tranpose_pointer += myCount*pieceLength;
        }

        for(currentSlice=0;currentSlice<SV_depth_modified;currentSlice++)
        {
            THETA1[currentSlice]=-THETA1[currentSlice]*Aval_max*(1.0/255);
            THETA2[currentSlice]=THETA2[currentSlice]*Aval_max*(1.0/255)*Aval_max*(1.0/255);
        }

        A_padd_Tranpose_pointer = &A_Padded_Map[SVPosition][theVoxelPosition].val[0];
        ETransposeArrayPointer = &newEArrayTransposed[0][0];

        for(currentSlice=0;currentSlice<SV_depth_modified;currentSlice++)
        if(zero_skip_FLAG[currentSlice] == 0)
        {
            float pixel,step;
            if(reconparams.ReconType == MBIR_MODULAR_RECONTYPE_QGGMRF_3D)
            {
                step = QGGMRF3D_Update(reconparams,param_ext,tempV[currentSlice],&neighbors[currentSlice][0],THETA1[currentSlice],THETA2[currentSlice]);
            }
            else if(reconparams.ReconType == MBIR_MODULAR_RECONTYPE_PandP)
            {
                step = PandP_Update(param_ext.SigmaXsq,tempV[currentSlice],tempProxMap[currentSlice],THETA1[currentSlice],THETA2[currentSlice]);
            }
            else
            {
                fprintf(stderr,"Error** Unrecognized ReconType in ICD update\n");
                exit(-1);
            }

            pixel = tempV[currentSlice] + (reconparams.RelaxFactor)*step;

            if(PositivityFlag)
                image[(size_t)(startSlice+currentSlice)*Nxy + j_new*Nx+k_new] = ((pixel < 0.0) ? 0.0 : pixel);
            else
                image[(size_t)(startSlice+currentSlice)*Nxy + j_new*Nx+k_new] = pixel;

            diff[currentSlice] = image[(size_t)(startSlice+currentSlice)*Nxy + j_new*Nx+k_new] - tempV[currentSlice];

            totalChange_loc += fabs(diff[currentSlice]);
            totalValue_loc += fabs(tempV[currentSlice]);
            NumUpdates_loc++;

            diff[currentSlice]=diff[currentSlice]*Aval_max*(1.0/255);
        }

        for(p=0;p<NViewSets;p++)
        {
            int myCount=A_Padded_Map[SVPosition][theVoxelPosition].pieceWiseWidth[p];
            int pieceMin=A_Padded_Map[SVPosition][theVoxelPosition].pieceWiseMin[p];
            #pragma vector aligned
            for(currentSlice=0;currentSlice<SV_depth_modified;currentSlice++)
            if(fabsf(diff[currentSlice])>0 && zero_skip_FLAG[currentSlice] == 0)
            {
                ETransposeArrayPointer=&newEArrayTransposed[p][currentSlice*bandWidth[p]*pieceLength];
                ETransposeArrayPointer+=pieceMin*pieceLength;

                #pragma vector aligned
                for(t=0;t<(myCount*pieceLength);t++)
                    ETransposeArrayPointer[t]= ETransposeArrayPointer[t]-A_padd_Tranpose_pointer[t]*diff[currentSlice];
            }
            A_padd_Tranpose_pointer+=myCount*pieceLength;
        }
    }

    free((void *)THETA1);
    free((void *)THETA2);
    free((void *)tempV);
    free((void *)diff);
    multifree(neighbors,2);
    free((void *)zero_skip_FLAG);
    if(reconparams.ReconType == MBIR_MODULAR_RECONTYPE_PandP)
        free((void *)tempProxMap);

    for (p = 0; p < NViewSets; p++)
        free((void *)newWArrayTransposed[p]);
    free((void **)newWArrayTransposed);

    free((void *)k_newCoordinate);
    free((void *)j_newCoordinate);

    for (p = 0; p < NViewSets; p++)
    for(currentSlice=0;currentSlice<SV_depth_modified;currentSlice++)
    {
        ETransposeArrayPointer=&newEArrayTransposed[p][currentSlice*bandWidth[p]*pieceLength];
        newEArrayPointer=&newEArray[p][currentSlice*bandWidth[p]*pieceLength];
        for(q=0;q<bandWidth[p];q++)
        {
            #pragma vector aligned
            for(t=0;t<pieceLength;t++)
                newEArrayPointer[bandWidth[p]*t+q]=ETransposeArrayPointer[q*pieceLength+t];
        }
    }

    for (p = 0; p < NViewSets; p++)
        free((void *)newEArrayTransposed[p]);
    free((void **)newEArrayTransposed);

    for (p = 0; p < NViewSets; p++)      /*XW: update the error term in the memory buffer*/
    {
        float *CopyNewEArrayPointer;
        float *eArrayPointer;
        newEArrayPointer=&newEArray[p][0];
        CopyNewEArrayPointer=&CopyNewEArray[p][0];
        for (currentSlice=0; currentSlice< SV_depth_modified;currentSlice++)
        {
            //#pragma vector aligned
            for(q=0;q<pieceLength;q++)
            {
                eArrayPointer=&sinoerr[(size_t)(startSlice+currentSlice)*Nvc+p*pieceLength*sinoparams.NChannels+q*sinoparams.NChannels+bandMin[p*pieceLength+q]];
                for(t=0;t<bandWidth[p];t++)
                {
                    #pragma omp atomic
                    *eArrayPointer += (*newEArrayPointer)-(*CopyNewEArrayPointer);
                    newEArrayPointer++;
                    CopyNewEArrayPointer++;
                    eArrayPointer++;
                }
            }
        }
    }

    for (p = 0; p < NViewSets; p++) {
        free((void *)newEArray[p]);
        free((void *)CopyNewEArray[p]);
    }
    free((void **)newEArray);
    free((void **)CopyNewEArray);

    free((void *)bandMin);
    free((void *)bandMax);
    free((void *)bandWidth);
    free((void *)bandWidthTemp);

    headNodeArray[jj_new].x=totalChange_loc/SV_depth_modified;
    *NumUpdates += NumUpdates_loc;
    *totalValue += totalValue_loc;
    *totalChange += totalChange_loc;

}   /* END super_voxel_recon() */




void coordinateShuffle(int *order1, int *order2,int len)
{
	int i, j, tmp1,tmp2;

	for (i = 0; i < len-1; i++)
	{
		j = i + (rand() % (len-i));
		tmp1 = order1[j];
		tmp2 = order2[j];
		order1[j] = order1[i];
		order2[j] = order2[i];
		order1[i] = tmp1;
		order2[i] = tmp2;
	}
}

void three_way_shuffle(long *order1, char *order2, struct heap_node *headNodeArray, int len)
{
	int i,j;
	long tmp_long;
	char tmp_char;
	float temp_x;

	for (i = 0; i < len-1; i++)
	{
		j = i + (rand() % (len-i));
		tmp_long = order1[j];
		order1[j] = order1[i];
		order1[i] = tmp_long;
		tmp_char = order2[j];
		order2[j] = order2[i];
		order2[i] = tmp_char;
		temp_x=headNodeArray[j].x;
		headNodeArray[j].x=headNodeArray[i].x;
		headNodeArray[i].x=temp_x;
	}
}



float MAPCostFunction3D(
    float *x,
    float *e,
    float *w,
    struct ImageParams3D imgparams,
    struct SinoParams3DParallel sinoparams,
    struct ReconParams reconparams,
    struct ParamExt param_ext)
{
    int i, M, j, jx, jy, jz, Nx, Ny, Nz, Nxy, plusx, minusx, plusy, plusz;
    float nloglike, nlogprior_nearest, nlogprior_diag, nlogprior_interslice, x0;

    M = sinoparams.NViews * sinoparams.NChannels ;
    Nx = imgparams.Nx;
    Ny = imgparams.Ny;
    Nz = imgparams.Nz;
    Nxy = Nx*Ny;

    nloglike = 0.0;
    for (i = 0; i <sinoparams.NSlices; i++)
    for (j = 0; j < M; j++)
        nloglike += e[(size_t)i*M+j]*w[(size_t)i*M+j]*e[(size_t)i*M+j];

    nloglike /= 2.0;
    nlogprior_nearest = 0.0;
    nlogprior_diag = 0.0;
    nlogprior_interslice = 0.0;

    for (jz = 0; jz < Nz; jz++)
    for (jy = 0; jy < Ny; jy++)
    for (jx = 0; jx < Nx; jx++)
    {
        plusx = jx + 1;
        plusx = ((plusx < Nx) ? plusx : 0);
        minusx = jx - 1;
        minusx = ((minusx < 0) ? Nx-1 : minusx);
        plusy = jy + 1;
        plusy = ((plusy < Ny) ? plusy : 0);
        plusz = jz + 1;
        plusz = ((plusz < Nz) ? plusz : 0);

        j = jy*Nx + jx;
        x0 = x[(size_t)jz*Nxy+j];

        nlogprior_nearest += QGGMRF_Potential((x0-x[(size_t)jz*Nxy+jy*Nx+plusx]),reconparams,param_ext);
        nlogprior_nearest += QGGMRF_Potential((x0-x[(size_t)jz*Nxy+plusy*Nx+jx]),reconparams,param_ext);
        nlogprior_diag += QGGMRF_Potential((x0-x[(size_t)jz*Nxy+plusy*Nx+minusx]),reconparams,param_ext);
        nlogprior_diag += QGGMRF_Potential((x0-x[(size_t)jz*Nxy+plusy*Nx+plusx]),reconparams,param_ext);
        nlogprior_interslice += QGGMRF_Potential((x0-x[(size_t)plusz*Nxy+jy*Nx+jx]),reconparams,param_ext);
    }

    return (nloglike + reconparams.b_nearest * nlogprior_nearest + reconparams.b_diag * nlogprior_diag + reconparams.b_interslice * nlogprior_interslice) ;
}


/* Forward projection using input SV system matrix */

void SVproject(
    float *proj,
    float *image,
    struct AValues_char **A_Padded_Map,
    float *Aval_max_ptr,
    struct ImageParams3D imgparams,
    struct SinoParams3DParallel sinoparams,
    struct SVParams svpar,
    char backproject_flag)
{
    size_t i;
    int jz;
    int Nx = imgparams.Nx;
    int Ny = imgparams.Ny;
    int Nz = imgparams.Nz;
    int NChannels = sinoparams.NChannels;
    int Nvc = sinoparams.NViews * sinoparams.NChannels;
    int SVLength = svpar.SVLength;
    int pieceLength = svpar.pieceLength;
    int SVsPerRow = svpar.SVsPerRow;
    int NViewSets = sinoparams.NViews/pieceLength;
    struct minStruct * bandMinMap = svpar.bandMinMap;

    /* initialize output */
    if(backproject_flag)
        for (i = 0; i < (size_t)Nx*Ny*Nz; i++)
            image[i] = 0.0;
    else
        for (i = 0; i < (size_t)Nvc*Nz; i++)
            proj[i] = 0.0;

    #pragma omp parallel for schedule(dynamic)
    for(jz=0;jz<Nz;jz++)
    {
        int jx,jy,k,r,p;

        for (jy = 0; jy < Ny; jy++)
        for (jx = 0; jx < Nx; jx++)
        {
            int SV_ind_y = jy/(2*SVLength-svpar.overlap);
            int SV_ind_x = jx/(2*SVLength-svpar.overlap);
            int SVPosition = SV_ind_y*SVsPerRow + SV_ind_x;

            int SV_jy = SV_ind_y*(2*SVLength-svpar.overlap);
            int SV_jx = SV_ind_x*(2*SVLength-svpar.overlap);
            int VoxelPosition = (jy-SV_jy)*(2*SVLength+1)+(jx-SV_jx);

            // The second condition should always be true
            if (A_Padded_Map[SVPosition][VoxelPosition].length > 0 && VoxelPosition < ((2*SVLength+1)*(2*SVLength+1)))
            {
                unsigned char* A_padd_Tr_ptr = &A_Padded_Map[SVPosition][VoxelPosition].val[0];
                float rescale = Aval_max_ptr[jy*Nx+jx]*(1.0/255);
                size_t image_idx = (size_t)jz*Nx*Ny + jy*Nx + jx;
                float xval = image[image_idx];

                for(p=0;p<NViewSets;p++)
                {
                    int myCount = A_Padded_Map[SVPosition][VoxelPosition].pieceWiseWidth[p];
                    int pieceWiseMin = A_Padded_Map[SVPosition][VoxelPosition].pieceWiseMin[p];
                    int position = p*pieceLength*NChannels + pieceWiseMin;

                    for(r=0;r<myCount;r++)
                    for(k=0;k<pieceLength;k++)
                    {
                        channel_t bandMin = bandMinMap[SVPosition].bandMin[p*pieceLength+k];
                        size_t proj_idx = (size_t)jz*Nvc + position + k*NChannels + bandMin + r;

                        if((pieceWiseMin + bandMin + r) >= NChannels || (position + k*NChannels + bandMin + r) >= Nvc ) {
                            fprintf(stderr,"SVproject() out of bounds: p %d r %d k %d\n",p,r,k);
                            fprintf(stderr,"SVproject() out of bounds: total_1 %d total_2 %d\n",pieceWiseMin+bandMin+r,position+k*NChannels+bandMin+r);
                            exit(-1);
                        }
                        else
                        {
                            if(backproject_flag)
                                image[image_idx] += A_padd_Tr_ptr[r*pieceLength+k]*rescale * proj[proj_idx];
                            else
                                proj[proj_idx] += A_padd_Tr_ptr[r*pieceLength+k]*rescale * xval;
                        }
                    }
                    A_padd_Tr_ptr += myCount*pieceLength;
                }
            }
        }
    }
}


/* Forward projection wrapper that first reads or computes SV matrix */

void forwardProject(
    float *proj,
    float *image,
    struct ImageParams3D imgparams,
    struct SinoParams3DParallel sinoparams,
    char *Amatrix_fname,
    char backproject_flag,
    char verboseLevel)
{
    int i,j;
    struct AValues_char **A_Padded_Map;
    float *Aval_max_ptr;
    struct SVParams svpar;

    /* print summary to stdout */
    if(verboseLevel>1)
    {
        fprintf(stdout,"forwardProject() -- build time: %s, %s\n", __DATE__, __TIME__);
        printSinoParams3DParallel(&sinoparams);
        printImageParams3D(&imgparams);
    }

    /* Initialize/allocate SV parameters */
    initSVParams(&svpar, imgparams, sinoparams);
    int Nsv = svpar.Nsv;
    int SVLength = svpar.SVLength;

    /* Read/compute/write System Matrix */
    A_Padded_Map = (struct AValues_char **)multialloc(sizeof(struct AValues_char),2,Nsv,(2*SVLength+1)*(2*SVLength+1));
    Aval_max_ptr = (float *) mget_spc(imgparams.Nx*imgparams.Ny,sizeof(float));
    if(Amatrix_fname != NULL)
    {
        if(verboseLevel>1)
            fprintf(stdout,"Reading system matrix...\n");
        readAmatrix(Amatrix_fname, A_Padded_Map, Aval_max_ptr, &imgparams, &sinoparams, svpar);
    }
    else
    {
        if(verboseLevel)
            fprintf(stdout,"Computing system matrix...\n");
        char * ImageReconMask = GenImageReconMask(&imgparams);
        A_comp(A_Padded_Map,Aval_max_ptr,svpar,&sinoparams,ImageReconMask,&imgparams);
        free((void *)ImageReconMask);
    }

    /* Project */
    if(verboseLevel>1)
    {
        if(backproject_flag)
            fprintf(stdout,"Back-projecting sinogram...\n");
        else
            fprintf(stdout,"Projecting image...\n");
    }
    SVproject(proj,image,A_Padded_Map,Aval_max_ptr,imgparams,sinoparams,svpar,backproject_flag);

    /* Free SV memory */
    for(i=0;i<Nsv;i++) {
        free((void *)svpar.bandMinMap[i].bandMin);
        free((void *)svpar.bandMaxMap[i].bandMax);
    }
    free((void *)svpar.bandMinMap);
    free((void *)svpar.bandMaxMap);

    /* Free system matrix */
    for(i=0;i<Nsv;i++)
    for(j=0;j<(2*SVLength+1)*(2*SVLength+1);j++)
    if(A_Padded_Map[i][j].length>0)
    {
        free((void *)A_Padded_Map[i][j].val);
        free((void *)A_Padded_Map[i][j].pieceWiseMin);
        free((void *)A_Padded_Map[i][j].pieceWiseWidth);
    }
    multifree(A_Padded_Map,2);
    free((void *)Aval_max_ptr);

}   /* END forwardProject() */



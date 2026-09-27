
#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <string.h>
//#include <time.h>
#include <sys/time.h>

#include "mbir_ct.h"
#include "MBIRModularDefs.h"
#include "MBIRModularUtils.h"
#include "allocate.h"
#include "A_comp.h"
#include "initialize.h"
#include "recon3d.h"

/* Internal Functions */
void readCmdLine(int argc, char *argv[], struct CmdLine *cmdline);
void procCmdLine(int argc, char *argv[], struct CmdLine *cmdline);
void printCmdLineUsage(char *ExecFileName);
int CmdLineHelpOption(char *string);
int setNumSliceDigits(char *basename, char *ext, int slice, struct SinoParams3DParallel *sinoparams, struct ImageParams3D *imgparams);
int NumSliceDigits(char *basename, char *ext, int slice);

int main(int argc, char *argv[])
{
    struct CmdLine cmdline;
    struct Image3D Image;
    struct Image3D ProxMap;
    struct Sino3DParallel sinogram;
    struct ReconParams reconparams;
    char fname[1064], *readmatrix_fname=NULL;
    struct timeval tm0,tm2;
    unsigned long long tdiff;
    float **proj;
    float *proximalmap;
    int jz,FirstSliceNumber,Ndigits;

    gettimeofday(&tm0,NULL);

    readCmdLine(argc, argv, &cmdline);
    if(cmdline.verboseLevel) {
        fprintf(stdout,"SUPER-VOXEL MBIR CT RECONSTRUCTION\n");
        fprintf(stdout,"%s -- build time: %s, %s\n", argv[0], __DATE__,  __TIME__);
    }
    procCmdLine(argc, argv, &cmdline);

    /* Read image/sino parameter files */
    ReadSinoParams3DParallel(cmdline.SinoParamsFile,&sinogram.sinoparams);
    ReadImageParams3D(cmdline.ImageParamsFile,&Image.imgparams);
    int NvNc = sinogram.sinoparams.NViews * sinogram.sinoparams.NChannels;
    int Nz = Image.imgparams.Nz;

    /* Compute/write A matrix only and EXIT */
    if(cmdline.writeAmatrixFlag)
    {
        sprintf(fname,"%s.2Dsvmatrix",cmdline.SysMatrixFile);
        AmatrixComputeToFile(Image.imgparams,sinogram.sinoparams,fname,cmdline.verboseLevel);
        return(0);
    }

    /* Compute/write projection only and EXIT */
    if(cmdline.writeProjectionFlag && !cmdline.reconFlag)
    {
        AllocateImageData3D(&Image);
        if(cmdline.verboseLevel)
            fprintf(stdout,"Reading image...\n");
        FirstSliceNumber = Image.imgparams.FirstSliceNumber;
        Ndigits = setNumSliceDigits(cmdline.InitImageFile,"2Dimgdata",FirstSliceNumber,&sinogram.sinoparams,&Image.imgparams);
        ReadImage3D(cmdline.InitImageFile,&Image);
        proj = (float **)multialloc(sizeof(float),2,Nz,NvNc);

        /* set input matrix filename pointer--used to determine whether to read or compute */
        if(cmdline.readAmatrixFlag) {
            sprintf(fname,"%s.2Dsvmatrix",cmdline.SysMatrixFile);
            readmatrix_fname = &fname[0];
        }
        forwardProject(&proj[0][0],&(Image.image[0][0]),Image.imgparams,sinogram.sinoparams,readmatrix_fname,0,cmdline.verboseLevel);
        if(cmdline.verboseLevel)
            fprintf(stdout,"Writing projection to file...\n");
        for(jz=0; jz<Nz; jz++) {
            sprintf(fname,"%s_slice%.*d.2Dprojection",cmdline.outputProjectionFile,Ndigits,jz+FirstSliceNumber);
            if( WriteFloatArray(fname,proj[jz],NvNc) ) {
                fprintf(stderr,"Error: can't open file %s for writing\n",fname);
                exit(-1);
            }
        }
        multifree(proj,2);
        FreeImageData3D(&Image);
        return(0);
    }

    /*** From this point we're in Reconstruction mode ***/

    /* The image parameters specify the relevant slice range to reconstruct, so re-set the  */
    /* relevant sinogram parameters so it pulls the correct slices and indexes them consistently */
    sinogram.sinoparams.NSlices = Image.imgparams.Nz;
    sinogram.sinoparams.FirstSliceNumber = Image.imgparams.FirstSliceNumber;
    FirstSliceNumber = Image.imgparams.FirstSliceNumber;

    /* Detect the number of slice number digits in input file names */
    Ndigits = setNumSliceDigits(cmdline.SinoDataFile,"2Dsinodata",FirstSliceNumber,&sinogram.sinoparams,&Image.imgparams);

    /* Allocate and read sinogram data */
    AllocateImageData3D(&Image);
    AllocateSinoData3DParallel(&sinogram);
    ReadSinoData3DParallel(cmdline.SinoDataFile, &sinogram);

    /* set input matrix filename pointer--used to determine whether to read or compute */
    if(cmdline.readAmatrixFlag) {
        sprintf(fname,"%s.2Dsvmatrix",cmdline.SysMatrixFile);
        readmatrix_fname = &fname[0];
    }

    /* Special case: Compute back projection and exit */
    if(cmdline.reconFlag == MBIR_MODULAR_RECONTYPE_ADJOINT) {
        forwardProject(sinogram.sino[0],Image.image[0],Image.imgparams,sinogram.sinoparams,readmatrix_fname,1,cmdline.verboseLevel);
        /* Write out reconstructed image(s) */
        if(cmdline.verboseLevel)
            fprintf(stdout,"Writing image files...\n");
        WriteImage3D(cmdline.ReconImageFile, &Image);
        FreeImageData3D(&Image);
        FreeSinoData3DParallel(&sinogram);
        return(0);
    }

    ReadReconParams(cmdline.ReconParamsFile,&reconparams);
    if(reconparams.ReconType != cmdline.reconFlag)
    {
        fprintf(stdout,"**\nWarning: \"PriorModel\" field in reconparams file doesn't agree with\n");
        fprintf(stdout,"Warning: what the command line is doing. Proceeding anyway.\n**\n");
        reconparams.ReconType = cmdline.reconFlag;
    }

    /* Read/compute sinogram weights */
    if(cmdline.SinoWeightsFileFlag)
    {
        ReadWeights3D(cmdline.SinoWeightsFile, &sinogram);
        reconparams.weightType = 0;
    }
    else if(reconparams.weightType < 1)	// if weightType is expecting file input, revert to default
        reconparams.weightType = 1;
    ComputeSinoWeights(sinogram,reconparams);  // either compute internally, or scale input by 1/SigmaY^2

    /* Initialize image state */
    if(cmdline.readInitImageFlag) {
        if(cmdline.verboseLevel)
            fprintf(stdout,"Reading initial image...\n");
        ReadImage3D(cmdline.InitImageFile,&Image);
    }
    else
    {
        /* Allocate and generate recon mask based on ROIRadius (implicitly coded into A matrix) */
        char * ImageReconMask = GenImageReconMask(&Image.imgparams);
        initConstImage(&Image, ImageReconMask, reconparams.InitImageValue, 0);
        free((void *)ImageReconMask);
    }

    /* Read projection of initial image if called for */
    if(cmdline.readInitProjectionFlag)
    {
        if(cmdline.verboseLevel)
            fprintf(stdout,"Reading projection of initial image...\n");
        proj = (float **)multialloc(sizeof(float),2,sinogram.sinoparams.NSlices,NvNc);
        for(jz=0;jz<Nz;jz++)
        {
            sprintf(fname,"%s_slice%.*d.2Dprojection",cmdline.inputProjectionFile,Ndigits,jz+FirstSliceNumber);
            if(ReadFloatArray(fname,proj[jz],NvNc)) {
                fprintf(stderr,"Error: can't read %s\n",fname);
                exit(-1);
            }
        }
    }
    else
    {
        proj = (float **)multialloc(sizeof(float),2,1,1);
        proj[0] = NULL;  // defined this way so the recon wrapper will compute projection internally
    }

    /* Read Proximal map if necessary */
    if(reconparams.ReconType == MBIR_MODULAR_RECONTYPE_PandP)
    {
        ProxMap.imgparams.Nx = Image.imgparams.Nx;
        ProxMap.imgparams.Ny = Image.imgparams.Ny;
        ProxMap.imgparams.Nz = Image.imgparams.Nz;
        ProxMap.imgparams.FirstSliceNumber = Image.imgparams.FirstSliceNumber;
        ProxMap.imgparams.NumSliceDigits = Image.imgparams.NumSliceDigits;
        AllocateImageData3D(&ProxMap);
        ReadImage3D(cmdline.ProxMapImageFile,&ProxMap);
        proximalmap = &(ProxMap.image[0][0]);  // *ptr to proximal map image
    }
    else
        proximalmap = NULL;

    /* Start Reconstruction */
    MBIRReconstruct(
        Image.image[0],
        sinogram.sino[0],
        sinogram.weight[0],
        proj[0],
        proximalmap,
        Image.imgparams,
        sinogram.sinoparams,
        reconparams,
        readmatrix_fname,
        cmdline.verboseLevel);

    /* Write out reconstructed image(s) */
    if(cmdline.verboseLevel)
        fprintf(stdout,"Writing image files...\n");
    WriteImage3D(cmdline.ReconImageFile, &Image);

    /* Write Projection of image state if called for */
    if(cmdline.writeProjectionFlag)
    {
        // If recon() computed initial projection internally, it doesn't have a pointer
        // to return final projection. For this case, will recompute projection here.
        if(proj[0]==NULL)
        {
            multifree(proj,2);
            proj = (float **)multialloc(sizeof(float),2,Nz,NvNc);
            forwardProject(&proj[0][0],&(Image.image[0][0]),Image.imgparams,sinogram.sinoparams,readmatrix_fname,0,cmdline.verboseLevel);
        }
        if(cmdline.verboseLevel)
            fprintf(stdout,"Writing projection to file...\n");
        for(jz=0; jz<Nz; jz++)
        {
            sprintf(fname,"%s_slice%.*d.2Dprojection",cmdline.outputProjectionFile,Ndigits,jz+FirstSliceNumber);
            if( WriteFloatArray(fname,proj[jz],NvNc) ) {
                fprintf(stderr,"Error: can't open file %s for writing\n",fname);
                exit(-1);
            }
        }
    }

    FreeImageData3D(&Image);
    FreeSinoData3DParallel(&sinogram);
    multifree(proj,2);
    if(reconparams.ReconType == MBIR_MODULAR_RECONTYPE_PandP)
        FreeImageData3D(&ProxMap);

    if(cmdline.verboseLevel) {
        gettimeofday(&tm2,NULL);
        tdiff = 1000 * (tm2.tv_sec - tm0.tv_sec) + (tm2.tv_usec - tm0.tv_usec) / 1000;
        fprintf(stdout,"Done. Total run time = %llu ms\n",tdiff);
    }
    return(0);
}


/* Read Command-line */
void readCmdLine(int argc, char *argv[], struct CmdLine *cmdline)
{
    char ch;
    
    /* set defaults */
    cmdline->SinoParamsFileFlag=0;
    cmdline->ImageParamsFileFlag=0;
    cmdline->ReconParamsFileFlag=0;
    cmdline->SinoDataFileFlag=0;
    cmdline->SinoWeightsFileFlag=0;
    cmdline->ReconImageFileFlag=0;
    cmdline->SysMatrixFileFlag=0;

    cmdline->reconFlag = MBIR_MODULAR_RECONTYPE_QGGMRF_3D;
    cmdline->readInitImageFlag=0;
    cmdline->readInitProjectionFlag=0;
    cmdline->writeProjectionFlag=0;

    cmdline->verboseLevel=1;

    /* Print usage statement if no arguments, or help argument given */
    if(argc==1 || CmdLineHelpOption(argv[1]))
    {
        //fprintf(stdout,"Printing usage statement for %s\n",argv[0]);
        printCmdLineUsage(argv[0]);
        exit(0);
    }
    
    /* get options */
    while ((ch = getopt(argc, argv, "bi:j:k:s:w:r:m:t:e:f:p:v:")) != EOF)
    {
        switch (ch)
        {
            case 'i':
            {
                cmdline->ImageParamsFileFlag=1;
                sprintf(cmdline->ImageParamsFile, "%s", optarg);
                break;
            }
            case 'j':
            {
                cmdline->SinoParamsFileFlag=1;
                sprintf(cmdline->SinoParamsFile, "%s", optarg);
                break;
            }
            case 'k':
            {
                cmdline->ReconParamsFileFlag=1;
                sprintf(cmdline->ReconParamsFile, "%s", optarg);
                break;
            }
            case 's':
            {
                cmdline->SinoDataFileFlag=1;
                sprintf(cmdline->SinoDataFile, "%s", optarg);
                break;
            }
            case 'w':
            {
                cmdline->SinoWeightsFileFlag=1;
                sprintf(cmdline->SinoWeightsFile, "%s", optarg);
                break;
            }
            case 'r':
            {
                cmdline->ReconImageFileFlag=1;
                sprintf(cmdline->ReconImageFile, "%s", optarg);
                break;
            }
            case 'm':
            {
                cmdline->SysMatrixFileFlag=1;
                sprintf(cmdline->SysMatrixFile, "%s", optarg);
                break;
            }
            case 't':
            {
                cmdline->readInitImageFlag=1;
                sprintf(cmdline->InitImageFile, "%s", optarg);
                break;
            }
            case 'e':
            {
                cmdline->readInitProjectionFlag=1;
                sprintf(cmdline->inputProjectionFile, "%s", optarg);
                break;
            }
            case 'f':
            {
                cmdline->writeProjectionFlag=1;
                sprintf(cmdline->outputProjectionFile, "%s", optarg);
                break;
            }
            case 'p':
            {
                if(cmdline->reconFlag != MBIR_MODULAR_RECONTYPE_ADJOINT)
                    cmdline->reconFlag = MBIR_MODULAR_RECONTYPE_PandP;
                sprintf(cmdline->ProxMapImageFile, "%s", optarg);
                break;
            }
            case 'b':
            {
                cmdline->reconFlag = MBIR_MODULAR_RECONTYPE_ADJOINT;
                break;
            }
            case 'v':
            {
                sscanf(optarg,"%hhi",&cmdline->verboseLevel);
                break;
            }
            default:
            {
                //fprintf(stderr,"%s: invalid option '%c'\n",argv[0],ch);  //getopt does this already
                fprintf(stderr,"Try '%s -help' for more information.\n",argv[0]);
                exit(-1);
                break;
            }
        }
    }
}


/* Process Command-line */
void procCmdLine(int argc, char *argv[], struct CmdLine *cmdline)
{
    if(cmdline->verboseLevel>1)
        fprintf(stdout,"Parsing command line...\n");

    /* Check for mandatory arguments */
    if(!cmdline->SinoParamsFileFlag || !cmdline->ImageParamsFileFlag){
        fprintf(stderr,"Error: Either sinoparams or imgparams (-i,-j) file wasn't specified\n");
        fprintf(stderr,"Try '%s -help' for more information.\n",argv[0]);
        exit(-1);
    }

    /* Determine what to do based on supplied options 
     * cmdline->reconFlag
     * cmdline->readInitImageFlag
     * cmdline->readInitProjectionFlag
     * cmdline->writeProjectionFlag
     */
    cmdline->readAmatrixFlag=0;
    cmdline->writeAmatrixFlag=0;

    if(cmdline->ReconImageFileFlag)  /* reconstruction mode */
    {
        if(cmdline->SysMatrixFileFlag)
            cmdline->readAmatrixFlag=1;

        if(cmdline->readInitProjectionFlag && !cmdline->readInitImageFlag)
            cmdline->readInitProjectionFlag = 0;

        if(!cmdline->SinoDataFileFlag)
        {
            fprintf(stderr,"Error: Input sinogram data files not specified\n");
            fprintf(stderr,"Try '%s -help' for more information.\n",argv[0]);
            exit(-1);
        }
        if(!cmdline->ReconParamsFileFlag && (cmdline->reconFlag != MBIR_MODULAR_RECONTYPE_ADJOINT) )
        {
            fprintf(stderr,"Error: Reconstruction parameter file not specified\n");
            fprintf(stderr,"Try '%s -help' for more information.\n",argv[0]);
            exit(-1);
        }
    }
    else  /* precompute matrix or project input image */
    {
        cmdline->reconFlag=0;
        cmdline->readInitProjectionFlag=0;

        if(cmdline->writeProjectionFlag && !cmdline->readInitImageFlag)
            cmdline->writeProjectionFlag = 0;

        if(cmdline->writeProjectionFlag && cmdline->readInitImageFlag)  /* projection mode */
        {
            if(cmdline->SysMatrixFileFlag)
                cmdline->readAmatrixFlag=1;
        }
        else /* pre-compute matrix */
        {
            if(cmdline->SysMatrixFileFlag)
                cmdline->writeAmatrixFlag=1;
            else
            {
                fprintf(stderr,"Error: From the given command options, not sure what you want to do.\n");
                fprintf(stderr,"Try '%s -help' for more information.\n",argv[0]);
                exit(-1);
            }
        }
    }

    /* Print output and check errors of above parsing sequence  */
    if(cmdline->verboseLevel>1)
    {
        if(cmdline->reconFlag)
        {
            fprintf(stdout,"-> will perform reconstruction ");
            if(cmdline->reconFlag == MBIR_MODULAR_RECONTYPE_QGGMRF_3D)
                fprintf(stdout,"(QGGMRF)\n");
            if(cmdline->reconFlag == MBIR_MODULAR_RECONTYPE_PandP)
                fprintf(stdout,"(Plug & Play)\n");
            if(cmdline->reconFlag == MBIR_MODULAR_RECONTYPE_ADJOINT)
                fprintf(stdout,"(Backproject only! No MBIR)\n");

            if(cmdline->readAmatrixFlag)
                fprintf(stdout,"-> will read system matrix from file\n");
            else
            {
                fprintf(stdout,"-> will compute system matrix\n");
                fprintf(stdout," *** NOTE if you precompute/store the system matrix, any further reconstruction\n");
                fprintf(stdout," *** with the same image/sinogram in-slice dimensions will execute MUCH faster.\n");
                fprintf(stdout," *** See help (-m option)\n");
            //  fprintf(stdout,"***80 columns*******************************************************************\n\n");
            }

            if(cmdline->reconFlag != MBIR_MODULAR_RECONTYPE_ADJOINT)
            {
                if(!cmdline->SinoWeightsFileFlag)
                    fprintf(stdout,"-> will compute sinogram weights internally (no file provided)\n");
                if(cmdline->readInitImageFlag)
                    fprintf(stdout,"-> will read initial condition from file(s)\n");
                if(cmdline->readInitProjectionFlag)
                    fprintf(stdout,"-> will read projection of initial condition\n");
                else
                    fprintf(stdout,"-> will compute forward projection of initial condition\n");
                if(cmdline->writeProjectionFlag)
                    fprintf(stdout,"-> will save projection of output image state to file(s)\n");
            }
        }
        else if(cmdline->writeAmatrixFlag || cmdline->writeProjectionFlag)
        {
            fprintf(stdout,"-> no reconstruction\n");
            if(cmdline->writeAmatrixFlag)
                fprintf(stdout,"-> will compute system matrix and write to file\n");
            if(cmdline->writeProjectionFlag)
                fprintf(stdout,"-> will compute projection and write to file(s)\n");
            if(cmdline->ReconParamsFileFlag || cmdline->SinoDataFileFlag || cmdline->SinoWeightsFileFlag || cmdline->readInitProjectionFlag)
                fprintf(stdout,"Note some command line options are being ignored.\n");
        }

        fprintf(stdout,"Filenames provided:\n");
        if(cmdline->SinoParamsFileFlag)
            fprintf(stdout,"   Sino params   = %s.sinoparams\n",cmdline->SinoParamsFile);
        if(cmdline->ImageParamsFileFlag)
            fprintf(stdout,"   Image params  = %s.imgparams\n",cmdline->ImageParamsFile);
        if(cmdline->ReconParamsFileFlag)
            fprintf(stdout,"   Recon params  = %s.reconparams\n",cmdline->ReconParamsFile);
        if(cmdline->SinoDataFileFlag)
            fprintf(stdout,"   Sinogram data = %s_sliceNNN.2Dsinodata\n",cmdline->SinoDataFile);
        if(cmdline->SinoWeightsFileFlag)
            fprintf(stdout,"   Weight data   = %s_sliceNNN.2Dweightdata\n",cmdline->SinoWeightsFile);
        if(cmdline->ReconImageFileFlag)
            fprintf(stdout,"   Output images = %s_sliceNNN.2Dimgdata\n",cmdline->ReconImageFile);
        if(cmdline->readInitImageFlag)
            fprintf(stdout,"   Initial image = %s_sliceNNN.2Dimgdata\n",cmdline->InitImageFile);
        if(cmdline->SysMatrixFileFlag)
            fprintf(stdout,"   System matrix = %s.2Dsvmatrix\n",cmdline->SysMatrixFile);
        if(cmdline->readInitProjectionFlag)
            fprintf(stdout,"   Initial projection = %s.2Dprojection\n",cmdline->inputProjectionFile);
        if(cmdline->writeProjectionFlag)
            fprintf(stdout,"   Output projection = %s_sliceNNN.2Dprojection\n",cmdline->outputProjectionFile);
    }
}



int NumSliceDigits(char *basename, char *ext, int slice)
{
    FILE *fp;
    char fname[1024];
    int Ndigits = MBIR_MODULAR_MAX_NUMBER_OF_SLICE_DIGITS;

    while(Ndigits > 0)
    {
        sprintf(fname,"%s_slice%.*d.%s",basename, Ndigits, slice, ext);
        //printf("%s\n",fname);
        if( (fp=fopen(fname,"r")) ) {
            fclose(fp);
            break;
        }
        else
            Ndigits--;
    }
    return(Ndigits);
}


int setNumSliceDigits(
    char *basename,
    char *ext,
    int slice,
    struct SinoParams3DParallel *sinoparams,
    struct ImageParams3D *imgparams)
{
    int Ndigits;
    if( (Ndigits = NumSliceDigits(basename,ext,slice)) > 0 )
    {
        sinoparams->NumSliceDigits = Ndigits;
        imgparams->NumSliceDigits = Ndigits;
    }
    else
    {
        fprintf(stderr,"Error: Can't determine number of slice digits from given input file.\n");
        fprintf(stderr,"* Looking for file with this format: %s_slice%d.%s\n",basename,slice,ext);
        fprintf(stderr,"* where the slice number can contain leading zeros but no spaces.\n");
        exit(-1);
    }
    return(Ndigits);
}


void printBanner(void)
{
    fprintf(stdout,"MBIR RECONSTRUCTION FOR 3D PARALLEL-BEAM CT\n");
    fprintf(stdout,"build time: %s, %s\n\n", __DATE__,  __TIME__);
}


void printCmdLineUsage(char *ExecFileName)
{
//  fprintf(stdout,"***80 columns*******************************************************************\n\n");
    fprintf(stdout,"Command Line Help\n\n");
    fprintf(stdout,"There are three forms for the command line. One pre-computes and stores the\n");
    fprintf(stdout,"system matrix (saves time for other reconstructions w/ same geometry).\n");
    fprintf(stdout,"The second reconstructs the input sinogram, and the third computes the\n");
    fprintf(stdout,"projection of an input image set.\n");
    fprintf(stdout,"\n");
    fprintf(stdout,"Pre-compute system matrix: (printed on multiple lines for clarity)\n");
    fprintf(stdout,"\n");
    fprintf(stdout,"  %s\n",ExecFileName);
    fprintf(stdout,"\t-i <filename>[.imgparams]    : Input image parameters\n");
    fprintf(stdout,"\t-j <filename>[.sinoparams]   : Input sinogram parameters\n");
    fprintf(stdout,"\t-m <filename>[.2Dsvmatrix]   : Output matrix file\n");
    fprintf(stdout,"\n");
//  fprintf(stdout,"***80 columns*******************************************************************\n\n");
    fprintf(stdout,"Perform reconstruction:\n");
    fprintf(stdout,"\n");
    fprintf(stdout,"  %s\n",ExecFileName);
    fprintf(stdout,"\t-i <filename>[.imgparams]    : Input image parameters\n");
    fprintf(stdout,"\t-j <filename>[.sinoparams]   : Input sinogram parameters\n");
    fprintf(stdout,"\t-k <filename>[.reconparams]  : Reconstruction parameters\n");
    fprintf(stdout,"\t-s <baseFilename>            : Input sinogram projection file(s)\n");
    fprintf(stdout,"\t-r <baseFilename>            : Output reconstruced image file(s)\n");
    fprintf(stdout,"    (following are optional)\n");
    fprintf(stdout,"\t-m <filename>[.2Dsvmatrix]   : INPUT matrix file (params must correspond!)\n");
    fprintf(stdout,"\t-w <baseFilename>            : Input sinogram weight file(s)\n");
    fprintf(stdout,"\t-t <baseFilename>            : Input initial condition image(s)\n");
    fprintf(stdout,"\t-e <baseFilename>            : Input projection of initial condition\n");
    fprintf(stdout,"\t-f <baseFilename>            : Output projection of final image state\n");
    fprintf(stdout,"\t-p <baseFilename>            : Proximal map image(s) for Plug & Play\n");
    fprintf(stdout,"\t                             : ** -p specifies to use proximal prior\n");
    fprintf(stdout,"\t                             : ** generally use with -t -e -f\n");
//  fprintf(stdout,"***80 columns*******************************************************************\n\n");
    fprintf(stdout,"\t-b                           : compute and output simple back projection rather than MBIR\n");
    fprintf(stdout,"\t-v <verbose level>           : 0:quiet, 1:status info (default), 2:more info\n");
    fprintf(stdout,"\n");
    fprintf(stdout,"Compute projection of input only:\n");
    fprintf(stdout,"\n");
    fprintf(stdout,"  %s\n",ExecFileName);
    fprintf(stdout,"\t-i <filename>[.imgparams]    : Input image parameters\n");
    fprintf(stdout,"\t-j <filename>[.sinoparams]   : Input sinogram parameters\n");
    fprintf(stdout,"\t-t <baseFilename>            : Input image set\n");
    fprintf(stdout,"\t-f <baseFilename>            : Output projection\n");
    fprintf(stdout,"    (following are optional)\n");
    fprintf(stdout,"\t-m <filename>[.2Dsvmatrix]   : INPUT matrix file (params must correspond!)\n");
    fprintf(stdout,"\n");
    fprintf(stdout,"In the above arguments, the exensions given in the '[]' symbols must be part of\n");
    fprintf(stdout,"the file names but should be omitted from the command line.\n");
    fprintf(stdout,"For all the arguments specifying <baseFilename>, the relevant 3D data is split\n");
    fprintf(stdout,"across files, one file per slice. The file naming convention is as follows,\n");
    fprintf(stdout,"depending on the data contents:\n");
    fprintf(stdout,"\n");
    fprintf(stdout,"\t<baseFilename>_slice<sliceIndex>.2Dimgdata\n");
    fprintf(stdout,"\t<baseFilename>_slice<sliceIndex>.2Dsinodata\n");
    fprintf(stdout,"\t<baseFilename>_slice<sliceIndex>.2Dweightdata\n");
    fprintf(stdout,"\t<baseFilename>_slice<sliceIndex>.2Dprojection\n");
    fprintf(stdout,"\n");
    fprintf(stdout,"where <sliceIndex> (skip '<>' symbols) is a non-negative integer including\n");
    fprintf(stdout,"leading zeros and no spaces (e.g. 0000 to 1023). The number of digits\n");
    fprintf(stdout,"is flexible (up to %d) but must be consistent.\n",MBIR_MODULAR_MAX_NUMBER_OF_SLICE_DIGITS);
    fprintf(stdout,"\n");
}


int CmdLineHelpOption(char *string)
{
    if((strcmp(string,"-h")==0)||(strcmp(string,"-help")==0)||(strcmp(string,"--help")==0)||(strcmp(string,"help")==0))
        return 1;
    else
        return 0;
}




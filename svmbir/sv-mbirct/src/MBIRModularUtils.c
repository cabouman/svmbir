
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "allocate.h"
#include "MBIRModularDefs.h"
#include "MBIRModularUtils.h"

#ifndef MSVC  /* dirname(), libgen.h not in MS Visual C++ */
#include <libgen.h>
#endif


/*************************************************/
/*  Utilities for reading/printing .param files  */
/*************************************************/

/* Print Sinogram parameters */
void printSinoParams3DParallel(struct SinoParams3DParallel *sinoparams)
{
    fprintf(stdout, "SINOGRAM PARAMETERS:\n");
    fprintf(stdout, " - Number of sinogram views per slice    = %d\n", sinoparams->NViews);
    fprintf(stdout, " - Number of detector channels per slice = %d\n", sinoparams->NChannels);
    fprintf(stdout, " - Number of slices                      = %d\n", sinoparams->NSlices);
    fprintf(stdout, " - First slice index (wrt file names)    = %d\n", sinoparams->FirstSliceNumber);
    fprintf(stdout, " - Spacing between detector channels     = %.4g\n", sinoparams->DeltaChannel);
    fprintf(stdout, " - Center of rotation offset             = %.3f (channels)\n", sinoparams->CenterOffset);
    fprintf(stdout, " - Spacing between slices                = %.4g\n", sinoparams->DeltaSlice);
}

/* Utility for reading 3D parallel beam sinogram parameters */
/* Returns 0 if no error occurs */
int ReadSinoParams3DParallel(
	char *basename,			/* Source base filename, i.e. <basename>.sinoparams */
	struct SinoParams3DParallel *sinoparams)  /* Sinogram params data structure */
{
	FILE *fp;
	char fname[1024];
	char tag[200], fieldname[200], fieldval_s[200], *ptr;
	char AngleListFname[1024]=" ";
	int i, Nlines;
	char Geometry_flag=0;

	/* set defaults, also used for error checking below */
	sinoparams->NViews=0;		/* Number of view angles */
	sinoparams->NChannels=-1;	/* Number of channels in detector */
	sinoparams->DeltaChannel=0.0;	/* Detector spacing (length) */
	sinoparams->NSlices=0;		/* Number of slices stored in Sino array */
	sinoparams->FirstSliceNumber=-1;	/* slice index coresponding to first slice in volume */
	sinoparams->DeltaSlice=0.0;	/* Spacing along slice direction */
	sinoparams->CenterOffset=0.0;	/* Offset of center-of-rotation ... */
	sinoparams->DistSourceDetector=-1.0;	/* (fanbeam only) distance from source to detectors */
	sinoparams->Magnification=-1.0;		/* (fanbeam only) source-dist-to-detectors / source-dist-to-isocenter */

	strcpy(fname,basename);
	strcat(fname,".sinoparams"); /* append file extension */
	if((fp=fopen(fname,"r")) == NULL) {
		fprintf(stderr,"ERROR in ReadSinoParams3DParallel: can't open file %s\n",fname);
		exit(-1);
	}

	Nlines=0;
	while(fgets(tag, 200, fp)!=NULL && Nlines<100)
		Nlines++;
	rewind(fp);
	//printf("Nlines=%d\n",Nlines);

	/* parse each line assuming a single ":" delimiter */
	for(i=0; i<Nlines; i++)
	{
		strcpy(fieldname," ");
		strcpy(fieldval_s," ");
		if(fgets(tag, 200, fp) == NULL)
			return(-1);
		ptr=strtok(tag,":\n\r");	// including the newline will keep it out of the last token
		if(ptr!=NULL) {
			//strcpy(fieldname,ptr);
			sscanf(ptr,"%s",fieldname);	// this won't include leading/trailing spaces, strcpy will
			ptr=strtok(NULL,":\n\r");
		}
		if(ptr!=NULL) sscanf(ptr,"%s",fieldval_s);
		//printf("|%s|%s|\n",fieldname,fieldval_s);

		if(strcmp(fieldname,"Geometry")==0)
		{
			Geometry_flag=1;
			if(strcmp(fieldval_s,"parallel")==0)
				sinoparams->Geometry = 0;
			else if(strcmp(fieldval_s,"fan-curved")==0)
				sinoparams->Geometry = 1;
			else if(strcmp(fieldval_s,"fan-flat")==0)
				sinoparams->Geometry = 2;
			else {
				fprintf(stderr,"Error in %s: Geometry value \"%s\" unrecognized\n",fname,fieldval_s);
				exit(-1);
			}
		}
		else if(strcmp(fieldname,"NChannels")==0)
		{
			sscanf(fieldval_s,"%d",&(sinoparams->NChannels));
		}
		else if(strcmp(fieldname,"NViews")==0)
		{
			sscanf(fieldval_s,"%d",&(sinoparams->NViews));
		}
		else if(strcmp(fieldname,"NSlices")==0)
		{
			sscanf(fieldval_s,"%d",&(sinoparams->NSlices));
		}
		else if(strcmp(fieldname,"DeltaChannel")==0)
		{
			sscanf(fieldval_s,"%f",&(sinoparams->DeltaChannel));
		}
		else if(strcmp(fieldname,"CenterOffset")==0)
		{
			sscanf(fieldval_s,"%f",&(sinoparams->CenterOffset));
		}
		else if(strcmp(fieldname,"DistSourceDetector")==0)
		{
			sscanf(fieldval_s,"%f",&(sinoparams->DistSourceDetector));
		}
		else if(strcmp(fieldname,"Magnification")==0)
		{
			sscanf(fieldval_s,"%f",&(sinoparams->Magnification));
		}
		else if(strcmp(fieldname,"DeltaSlice")==0)
		{
			sscanf(fieldval_s,"%f",&(sinoparams->DeltaSlice));
		}
		else if(strcmp(fieldname,"FirstSliceNumber")==0)
		{
			sscanf(fieldval_s,"%d",&(sinoparams->FirstSliceNumber));
		}
		else if(strcmp(fieldname,"ViewAngleList")==0)
			sscanf(fieldval_s,"%s",AngleListFname);  // this won't include leading/trailing spaces, strcpy will
			//strcpy(AngleListFname,fieldval_s);
		else
			fprintf(stderr,"Warning: unrecognized field \"%s\" in %s, line %d\n",fieldname,fname,i+1);

	}  // done parsing

	fclose(fp);

	//printSinoParams3DParallel(sinoparams);

	/* do some error checking */
	if(Geometry_flag==0) {
		fprintf(stderr,"Error in %s: \"Geometry\" field unspecified\n",fname);
		exit(-1);
	}
	if(sinoparams->Geometry > 0) {
		if(sinoparams->DistSourceDetector < 0.0 || sinoparams->Magnification < 0.0) {
			fprintf(stderr,"Error in %s: Invalid/unspecified DistSourceDetector or Magnification\n",fname);
			exit(-1);
		}
	}
	if(sinoparams->NViews<=0 || sinoparams->NChannels<=0 || sinoparams->NSlices<=0) {
		printSinoParams3DParallel(sinoparams);
		fprintf(stderr,"Error in %s: NViews, NChannels, NSlices must all be positive\n",fname);
		exit(-1);
	}
	if(sinoparams->DeltaChannel<=0 && sinoparams->NChannels>1) {
		printSinoParams3DParallel(sinoparams);
		fprintf(stderr,"Error in %s: DeltaChannel needs to be positive\n",fname);
		exit(-1);
	}
	if(sinoparams->DeltaSlice<=0 && sinoparams->NSlices>1) {
		printSinoParams3DParallel(sinoparams);
		fprintf(stderr,"Error in %s: DeltaSlice needs to be positive\n",fname);
		exit(-1);
	}
	if(sinoparams->FirstSliceNumber < 0) {
		printSinoParams3DParallel(sinoparams);
		fprintf(stderr,"Error in %s: FirstSliceNumber should be non-negative\n",fname);
		exit(-1);
	}

	/* form full pathname of ViewAngleList file; path relative to sinoparams directory */
	strcpy(fieldval_s,AngleListFname);  // tmp copy
	#ifdef MSVC  /* dirname(), libgen.h not in MS Visual C++ */
	char tmp_drive[1024],tmp_path[1024];
	_splitpath_s(fname,tmp_drive,1024,tmp_path,1024,NULL,0,NULL,0);
	sprintf(AngleListFname,"%s%s%s",tmp_drive,tmp_path,fieldval_s);
	#else
	strcpy(tag,fname);	// fname contains sinoparams full path filename
	ptr=dirname(tag);
	sprintf(AngleListFname,"%s/%s",ptr,fieldval_s);
	#endif
	//printf("Views filename \"%s\"\n",AngleListFname);

	/* Read the view angles file */
	if((fp=fopen(AngleListFname,"r")) == NULL) {
		fprintf(stderr,"ERROR in ReadSinoParams3DParallel: can't open ViewAngle file %s\n",AngleListFname);
		exit(-1);
	}

	sinoparams->ViewAngles = (float *)get_spc(sinoparams->NViews, sizeof(float));

	for(i=0;i<sinoparams->NViews;i++)
	if(fscanf(fp,"%f\n",&(sinoparams->ViewAngles[i])) == 0) {
		fprintf(stderr, "ERROR in ReadSinoParams3DParallel: View angles file %s terminated early\n", AngleListFname);
		exit(-1);
	}

	fclose(fp);

	return(0);
}


/* Print Image parameters */
void printImageParams3D(struct ImageParams3D *imgparams)
{
    fprintf(stdout, "IMAGE PARAMETERS:\n");
    fprintf(stdout, " - Number of pixels per slice in (X,Y)-directions    = (%d,%d)\n",imgparams->Nx,imgparams->Ny);
    fprintf(stdout, " - Number of slices (to reconstruct if output param) = %d\n",imgparams->Nz);
    fprintf(stdout, " - First slice index (wrt sino/img file names)       = %d\n",imgparams->FirstSliceNumber);
    fprintf(stdout, " - Pixel width in XY plane               = %.4g\n", imgparams->Deltaxy);
    fprintf(stdout, " - Spacing between slices                = %.4g\n", imgparams->DeltaZ);
    fprintf(stdout, " - ROIRadius                             = %.4g\n", imgparams->ROIRadius);
}

/* Utility for reading 2D Image parameters */
/* Returns 0 if no error occurs */
int ReadImageParams3D(
	char *basename,		/* Source base filename, i.e. <basename>.imgparams */
	struct ImageParams3D *imgparams)  /* Image params data structure */
{
	FILE *fp;
	char fname[1024];
	char tag[200], fieldname[200], fieldval_s[200], *ptr;
	int i, Nlines;

	/* set defaults, also used for error checking below */
	imgparams->Nx=0;
	imgparams->Ny=0;
	imgparams->Nz=0;
	imgparams->FirstSliceNumber=-1;
	imgparams->Deltaxy=0.0;
	imgparams->DeltaZ=0;
	imgparams->ROIRadius=0.0;

	strcpy(fname,basename);
	strcat(fname,".imgparams");
	if((fp=fopen(fname,"r")) == NULL) {
		fprintf(stderr,"ERROR in ReadImageParams3D: can't open file %s\n",fname);
		exit(-1);
	}

	Nlines=0;
	while(fgets(tag, 200, fp)!=NULL && Nlines<100)
		Nlines++;
	rewind(fp);
	//printf("Nlines=%d\n",Nlines);

	/* parse each line assuming a single ":" delimiter */
	for(i=0; i<Nlines; i++)
	{
		strcpy(fieldname," ");
		strcpy(fieldval_s," ");
		if(fgets(tag, 200, fp) == NULL)
			return(-1);
		ptr=strtok(tag,":\n\r");	// including the newline will keep it out of the last token
		if(ptr!=NULL) {
			//strcpy(fieldname,ptr);
			sscanf(ptr,"%s",fieldname);	// this won't include leading/trailing spaces, strcpy will
			ptr=strtok(NULL,":\n\r");
		}
		if(ptr!=NULL) sscanf(ptr,"%s",fieldval_s);
		//printf("|%s|%s|\n",fieldname,fieldval_s);

		if(strcmp(fieldname,"Nx")==0)
		{
			sscanf(fieldval_s,"%d",&(imgparams->Nx));
		}
		else if(strcmp(fieldname,"Ny")==0)
		{
			sscanf(fieldval_s,"%d",&(imgparams->Ny));
		}
		else if(strcmp(fieldname,"Nz")==0)
		{
			sscanf(fieldval_s,"%d",&(imgparams->Nz));
		}
		else if(strcmp(fieldname,"FirstSliceNumber")==0)
		{
			sscanf(fieldval_s,"%d",&(imgparams->FirstSliceNumber));
		}
		else if(strcmp(fieldname,"Deltaxy")==0)
		{
			sscanf(fieldval_s,"%f",&(imgparams->Deltaxy));
		}
		else if(strcmp(fieldname,"DeltaZ")==0)
		{
			sscanf(fieldval_s,"%f",&(imgparams->DeltaZ));
		}
		else if(strcmp(fieldname,"ROIRadius")==0)
		{
			sscanf(fieldval_s,"%f",&(imgparams->ROIRadius));
		}
		else
			fprintf(stderr,"Warning: unrecognized field \"%s\" in %s, line %d\n",fieldname,fname,i+1);

	}  // done parsing

	fclose(fp);

	//printImageParams3D(imgparams);

	/* do some error checking */
	if(imgparams->Nx<=0 || imgparams->Ny<=0 || imgparams->Nz<=0) {
		printImageParams3D(imgparams);
		fprintf(stderr,"Error in %s: Nx, Ny, Nz must all be positive\n",fname);
		exit(-1);
	}
	if(imgparams->Deltaxy<=0) {
		printImageParams3D(imgparams);
		fprintf(stderr,"Error in %s: Deltaxy needs to be positive\n",fname);
		exit(-1);
	}
	if(imgparams->DeltaZ<=0 && imgparams->Nz>1) {
		printImageParams3D(imgparams);
		fprintf(stderr,"Error in %s: DeltaZ needs to be positive\n",fname);
		exit(-1);
	}
	if(imgparams->FirstSliceNumber < 0) {
		printImageParams3D(imgparams);
		fprintf(stderr,"Error in %s: FirstSliceNumber should be non-negative\n",fname);
		exit(-1);
	}
	if(imgparams->ROIRadius<=0) {
		imgparams->ROIRadius = imgparams->Nx * imgparams->Deltaxy;
		fprintf(stderr,"Warning in %s: ROIRadius needs to be positive. Defaulting to %.4g\n",fname,imgparams->ROIRadius);
		printImageParams3D(imgparams);
	}

	return(0);
}


/* Print QGGMRF reconstruction parameters */
void printReconParamsQGGMRF3D(struct ReconParams *reconparams)
{
    fprintf(stdout, "RECONSTRUCTION/PRIOR PARAMETERS:\n");
    fprintf(stdout, " - Prior Type                                            = QGGMRF\n");
    fprintf(stdout, " - Q-GGMRF Prior Parameter, q                            = %.2f\n", reconparams->p);
    fprintf(stdout, " - Q-GGMRF Prior Parameter, p                            = %.2f\n", reconparams->q);
    fprintf(stdout, " - Q-GGMRF Prior Parameter, T                            = %.4g\n", reconparams->T);
    fprintf(stdout, " - Prior Regularization parameter, SigmaX                = %.4g\n", reconparams->SigmaX);
    fprintf(stdout, " - Scaling for sino weights, SigmaY (W <- W/SigmaY^2)    = %.4g\n", reconparams->SigmaY);
    fprintf(stdout, " - Prior weight for nearest neighbors within slice       = %.3f\n", reconparams->b_nearest);
    fprintf(stdout, " - Prior weight for diagonal neighbors within slice      = %.3f\n", reconparams->b_diag);
    fprintf(stdout, " - Prior weight for nearest neighbors in adjacent slices = %.3f\n", reconparams->b_interslice);
    fprintf(stdout, " - Inital image value                                    = %-10f\n", reconparams->InitImageValue);
    fprintf(stdout, " - Stop threshold for convergence                        = %.6f %%\n", reconparams->StopThreshold);
    fprintf(stdout, " - Maximum number of ICD iterations                      = %d\n", reconparams->MaxIterations);
    fprintf(stdout, " - Positivity constraint flag                            = %d\n", reconparams->Positivity);
    fprintf(stdout, " - Relaxation Factor                                     = %.2f\n", reconparams->RelaxFactor);
}
/* Print PandP reconstruction parameters */
void printReconParamsPandP(struct ReconParams *reconparams)
{
    fprintf(stdout, "RECONSTRUCTION/PRIOR PARAMETERS:\n");
    fprintf(stdout, " - Prior Type                                            = Plug & Play\n");
    fprintf(stdout, " - Regularization parameter for Proximal Map, SigmaX     = %.4g\n", reconparams->SigmaX);
    fprintf(stdout, " - Scaling for sino weights, SigmaY (W <- W/SigmaY^2)    = %.4g\n", reconparams->SigmaY);
    fprintf(stdout, " - Stop threshold for convergence                        = %.7f %%\n", reconparams->StopThreshold);
    fprintf(stdout, " - Maximum number of ICD iterations                      = %d\n", reconparams->MaxIterations);
    fprintf(stdout, " - Positivity constraint flag                            = %d\n", reconparams->Positivity);
}

/* Utility for reading reconstruction parameter files */
/* Returns 0 if no error occurs */
int ReadReconParams(
	char *basename,				/* Source base filename, i.e. <basename>.reconparams */
	struct ReconParams *reconparams)  /* Reconstruction parameters data structure */
{
	FILE *fp;
	char fname[1024];
	char tag[200], fieldname[200], fieldval_s[200], *ptr;
	double fieldval_f;
	int fieldval_d;
	int i, Nlines;
	char Prior_flag=0;

	/* set defaults, also used for error checking below */
	reconparams->InitImageValue=MUWATER;
	//reconparams->InitImageValue=0.0;
	reconparams->StopThreshold=1.0;
	reconparams->MaxIterations=20;
	reconparams->Positivity=1;
	reconparams->RelaxFactor=1.0;

	reconparams->b_nearest=1.0;
	reconparams->b_diag=0.707;
	reconparams->b_interslice=1.0;

	reconparams->p=1.2;
	reconparams->q=2.0;
	reconparams->T=0.1;
	reconparams->SigmaX=0.02;
	reconparams->SigmaY=1.0;
	reconparams->weightType=1;	// uniform by default

	strcpy(fname,basename);
	strcat(fname,".reconparams");
	if((fp=fopen(fname,"r")) == NULL) {
		fprintf(stderr,"ERROR in ReadReconParams: can't open file %s\n",fname);
		exit(-1);
	}

	Nlines=0;
	while(fgets(tag, 200, fp)!=NULL && Nlines<100)
		Nlines++;
	rewind(fp);
	//printf("Nlines=%d\n",Nlines);

	/* parse each line assuming a single ":" delimiter */
	for(i=0; i<Nlines; i++)
	{
		strcpy(fieldname," ");
		strcpy(fieldval_s," ");
		if(fgets(tag, 200, fp) == NULL)
			return(-1);
		ptr=strtok(tag,":\n\r");	// including the newline will keep it out of the last token
		if(ptr!=NULL) {
			//strcpy(fieldname,ptr);
			sscanf(ptr,"%s",fieldname);	// this won't include leading/trailing spaces, strcpy will
			ptr=strtok(NULL,":\n\r");
		}
		if(ptr!=NULL) sscanf(ptr,"%s",fieldval_s);
		//printf("|%s|%s|\n",fieldname,fieldval_s);

		if(strcmp(fieldname,"PriorModel")==0)
		{
			Prior_flag=1;
			if(strcmp(fieldval_s,"QGGMRF")==0)
				reconparams->ReconType = MBIR_MODULAR_RECONTYPE_QGGMRF_3D;
			else if(strcmp(fieldval_s,"PandP")==0)
				reconparams->ReconType = MBIR_MODULAR_RECONTYPE_PandP;
			else
			{
				fprintf(stderr,"Error in %s: PriorModel value \"%s\" unrecognized\n",fname,fieldval_s);
				exit(-1);
			}
		}
		else if(strcmp(fieldname,"InitImageValue")==0)
		{
			//sscanf(fieldval_s,"%lf",&(reconparams->InitImageValue));
			//Changed above to the following to retain default value if input doesn't make sense
			sscanf(fieldval_s,"%lf",&(fieldval_f));
			//if(fieldval_f < 0)
			//	fprintf(stderr,"Warning in %s: InitImageValue should be non-negative. Reverting to default.\n",fname);
			//else
			reconparams->InitImageValue = fieldval_f;
		}
		else if(strcmp(fieldname,"p")==0)
		{
			sscanf(fieldval_s,"%lf",&(fieldval_f));
			if(fieldval_f < 1 || fieldval_f > 2)
				fprintf(stderr,"Warning in %s: p parameter should be in range [1,2]. Reverting to default.\n",fname);
			else
				reconparams->p = fieldval_f;
		}
		else if(strcmp(fieldname,"q")==0)
		{
			sscanf(fieldval_s,"%lf",&(fieldval_f));
			if(fieldval_f < 1 || fieldval_f > 2)
				fprintf(stderr,"Warning in %s: q parameter should be in range [1,2]. Reverting to default.\n",fname);
			else
				reconparams->q = fieldval_f;
		}
		else if(strcmp(fieldname,"T")==0)
		{
			sscanf(fieldval_s,"%lf",&(fieldval_f));
			if(fieldval_f <= 0)
				fprintf(stderr,"Warning in %s: T parameter should be positive. Reverting to default.\n",fname);
			else
				reconparams->T = fieldval_f;
		}
		else if(strcmp(fieldname,"SigmaX")==0)
		{
			sscanf(fieldval_s,"%lf",&(fieldval_f));
			if(fieldval_f <= 0)
				fprintf(stderr,"Warning in %s: SigmaX parameter should be positive. Reverting to default.\n",fname);
			else
				reconparams->SigmaX = fieldval_f;
		}
		else if(strcmp(fieldname,"SigmaY")==0)
		{
			sscanf(fieldval_s,"%lf",&(fieldval_f));
			if(fieldval_f <= 0)
				fprintf(stderr,"Warning in %s: SigmaY parameter should be positive. Reverting to default.\n",fname);
			else
				reconparams->SigmaY = fieldval_f;
		}
		else if(strcmp(fieldname,"weightType")==0)
		{
			sscanf(fieldval_s,"%d",&(fieldval_d));
			if((fieldval_d < 0) || (fieldval_d > 4))
				fprintf(stderr,"Warning in %s: Valid weightType vals are 0,1,2,3,4. Reverting to default.\n",fname);
			else
				reconparams->weightType = fieldval_d;
		}
		else if(strcmp(fieldname,"b_nearest")==0)
		{
			sscanf(fieldval_s,"%lf",&(fieldval_f));
			if(fieldval_f <= 0)
				fprintf(stderr,"Warning in %s: b_nearest parameter should be positive. Reverting to default.\n",fname);
			else
				reconparams->b_nearest = fieldval_f;
		}
		else if(strcmp(fieldname,"b_diag")==0)
		{
			sscanf(fieldval_s,"%lf",&(fieldval_f));
			if(fieldval_f < 0)
				fprintf(stderr,"Warning in %s: b_diag parameter should be non-negative. Reverting to default.\n",fname);
			else
				reconparams->b_diag = fieldval_f;
		}
		else if(strcmp(fieldname,"b_interslice")==0)
		{
			sscanf(fieldval_s,"%lf",&(fieldval_f));
			if(fieldval_f < 0)
				fprintf(stderr,"Warning in %s: b_interslice parameter should be non-negative. Reverting to default.\n",fname);
			else
				reconparams->b_interslice = fieldval_f;
		}
		else if(strcmp(fieldname,"StopThreshold")==0)
		{
			sscanf(fieldval_s,"%lf",&(fieldval_f));
			if(fieldval_f < 0)
				fprintf(stderr,"Warning in %s: StopThreshold should be non-negative. Reverting to default.\n",fname);
			else
				reconparams->StopThreshold = fieldval_f;
		}
		else if(strcmp(fieldname,"MaxIterations")==0)
		{
			sscanf(fieldval_s,"%d",&(fieldval_d));
			if(fieldval_d < 1)
				fprintf(stderr,"Warning in %s: MaxIterations should be at least 1. Reverting to default.\n",fname);
			else
				reconparams->MaxIterations = fieldval_d;
		}
		else if(strcmp(fieldname,"Positivity")==0)
		{
			sscanf(fieldval_s,"%d",&(fieldval_d));
			if( strcmp(fieldval_s,"0") && strcmp(fieldval_s,"1") )
				fprintf(stderr,"Warning in %s: \"Positivity\" parameter options are 0/1. Reverting to default.\n",fname);
			else
				reconparams->Positivity = fieldval_d;
		}
		else if(strcmp(fieldname,"RelaxFactor")==0)
		{
			sscanf(fieldval_s,"%lf",&(fieldval_f));
			if((fieldval_f <= 0.0) || (fieldval_f > 2.0))
				fprintf(stderr,"Warning in %s: RelaxFactor outside valid range. Reverting to default value 1.0.\n",fname);
			else
				reconparams->RelaxFactor = fieldval_f;
		}
		else
			fprintf(stderr,"Warning: unrecognized field \"%s\" in %s, line %d\n",fieldname,fname,i+1);

	}  // done parsing

	fclose(fp);

	/* do some error checking */
	if(Prior_flag==0) {
		fprintf(stderr,"Error in %s: \"PriorModel\" field unspecified\n",fname);
		exit(-1);
	}
	if(reconparams->p > reconparams->q) {
		printReconParamsQGGMRF3D(reconparams);
		fprintf(stderr,"Error in %s: Need (p <= q) for convexity. (p<q for strict convexity)\n",fname);
		exit(-1);
	}

	return(0);
}


/*******************************/
/*     General purpose I/O     */
/*******************************/

/* General purpose utility for reading array of floats from a file */
/* Exit codes:							*/
/*   0 = success						*/
/*   1 = failure: can't open file				*/
/*   2 = failure: read from file terminated early		*/
int ReadFloatArray(
	char *fname,	/* source filename */
	float *array,	/* pointer to destination */
	int N)		/* Number of single precision elements to read */
{
	FILE *fp;
        if( (fp = fopen(fname,"rb")) == NULL )
           return(1);
        if(fread(array,sizeof(float),N,fp) != (size_t)N) {
           fclose(fp);
           return(2);
	}
        fclose(fp);
	return(0);
}

/* General purpose utility for writing array of floats to a file */
/* Exit codes:							*/
/*   0 = success						*/
/*   1 = failure: can't open file				*/
/*   2 = failure: write to file terminated early		*/
int WriteFloatArray(
	char *fname,	/* destination filename */
	float *array,	/* pointer to source array */
	int N)		/* Number of single precision elements to write */
{
	FILE *fp;
        if( (fp = fopen(fname,"wb")) == NULL )
           return(1);
        if(fwrite(array,sizeof(float),N,fp) != (size_t)N) {
           fclose(fp);
           return(2);
	}
        fclose(fp);
	return(0);
}


/**********************************************/
/*     Sinogram I/O and memory allocation     */
/**********************************************/

/* Utility for reading 3D parallel beam sinogram data */
/* Warning: Memory must be allocated before use */
/* Returns 0 if no error occurs */
int ReadSinoData3DParallel(
    char *basename,	/* Source base filename, i.e. <basename>_slice<Index>.2Dsinodata for given index range */
    struct Sino3DParallel *sinogram)  /* Sinogram data+params data structure */
{
    char fname[1024];
    int i,NSlices,FirstSliceNumber,M,exitcode;
    
    NSlices = sinogram->sinoparams.NSlices;
    FirstSliceNumber = sinogram->sinoparams.FirstSliceNumber;
    M = sinogram->sinoparams.NViews * sinogram->sinoparams.NChannels;
    
    for(i=0;i<NSlices;i++)
    {
        sprintf(fname,"%s_slice%.*d.2Dsinodata",basename, sinogram->sinoparams.NumSliceDigits, i+FirstSliceNumber);
        //sprintf(fname,"%s_slice%.*d.2Dsinodata",basename,MBIR_MODULAR_MAX_NUMBER_OF_SLICE_DIGITS,i+FirstSliceNumber);
        //printf("filename: |%s|\n",fname);
        
        if( (exitcode=ReadFloatArray(fname,sinogram->sino[i],M)) ) {
            if(exitcode==1)
                fprintf(stderr, "ERROR in ReadSinoData3DParallel: can't open file %s\n",fname);
            if(exitcode==2)
                fprintf(stderr, "ERROR in ReadSinoData3DParallel: read from file %s terminated early\n",fname);
            exit(-1);
        }
    }
    return 0;
}


/* Utility for reading weights for 3D sinogram projections data */
/* Warning: Memory must be allocated before use */
/* Returns 0 if no error occurs */
int ReadWeights3D(
	char *basename,		/* Source base filename, i.e. <basename>_slice<Index>.2Dweightdata for given index range */
	struct Sino3DParallel *sinogram)  /* Sinogram data+params data structure */
{
    char fname[1024];
    int i,NSlices,FirstSliceNumber,M,exitcode;

    NSlices = sinogram->sinoparams.NSlices;
    FirstSliceNumber = sinogram->sinoparams.FirstSliceNumber;
    M = sinogram->sinoparams.NViews * sinogram->sinoparams.NChannels;

    for(i=0;i<NSlices;i++)
    {
        sprintf(fname,"%s_slice%.*d.2Dweightdata",basename, sinogram->sinoparams.NumSliceDigits, i+FirstSliceNumber);
        //sprintf(fname,"%s_slice%.*d.2Dweightdata",basename,MBIR_MODULAR_MAX_NUMBER_OF_SLICE_DIGITS,i+FirstSliceNumber);
        //printf("filename: |%s|\n",fname);
        
        if( (exitcode=ReadFloatArray(fname,sinogram->weight[i],M)) ) {
            if(exitcode==1)
                fprintf(stderr, "ERROR in ReadWeights3D: can't open file %s\n",fname);
            if(exitcode==2)
                fprintf(stderr, "ERROR in ReadWeights3D: read from file %s terminated early\n",fname);
            exit(-1);
        }
    }
    return 0;
}


/* Utility for writing out 3D parallel beam sinogram parameters and data */
/* Returns 0 if no error occurs */
int WriteSino3DParallel(
    char *basename,	/* Input: Writes sinogram data to <basename>_slice<n>.2Dsinodata for given slice range */
    struct Sino3DParallel *sinogram)  /* Input: Sinogran parameters and data */
{
    char fname[1024];
    int i,NSlices,FirstSliceNumber,M,exitcode;

    NSlices = sinogram->sinoparams.NSlices;
    FirstSliceNumber = sinogram->sinoparams.FirstSliceNumber;
    M = sinogram->sinoparams.NViews * sinogram->sinoparams.NChannels;

    for(i=0;i<NSlices;i++)
    {
        sprintf(fname,"%s_slice%.*d.2Dsinodata",basename, sinogram->sinoparams.NumSliceDigits, i+FirstSliceNumber);
        //sprintf(fname,"%s_slice%.*d.2Dsinodata",basename,MBIR_MODULAR_MAX_NUMBER_OF_SLICE_DIGITS,i+FirstSliceNumber);
        //printf("filename: |%s|\n",fname);
        
        if( (exitcode=WriteFloatArray(fname,sinogram->sino[i],M)) ) {
            if(exitcode==1)
                fprintf(stderr, "ERROR in WriteSino3DParallel: can't open file %s\n",fname);
            if(exitcode==2)
                fprintf(stderr, "ERROR in WriteSino3DParallel: write to file %s terminated early\n",fname);
            exit(-1);
        }
    }
    return 0;
}


/* Utility for writing out weights for 3D parallel beam sinogram data */
/* Returns 0 if no error occurs */
int WriteWeights3D(
    char *basename,	/* Destination base filename, i.e. <basename>_slice<Index>.2Dweightdata for given index range */
    struct Sino3DParallel *sinogram)  /* Sinogram data+params data structure */
{
    char fname[1024];
    int i,NSlices,FirstSliceNumber,M,exitcode;

    NSlices = sinogram->sinoparams.NSlices;
    FirstSliceNumber = sinogram->sinoparams.FirstSliceNumber;
    M = sinogram->sinoparams.NViews * sinogram->sinoparams.NChannels;

    for(i=0;i<NSlices;i++)
    {
        sprintf(fname,"%s_slice%.*d.2Dweightdata",basename, sinogram->sinoparams.NumSliceDigits, i+FirstSliceNumber);
        //sprintf(fname,"%s_slice%.*d.2Dweightdata",basename,MBIR_MODULAR_MAX_NUMBER_OF_SLICE_DIGITS,i+FirstSliceNumber);
        //printf("filename: |%s|\n",fname);
        
        if( (exitcode=WriteFloatArray(fname,sinogram->weight[i],M)) ) {
            if(exitcode==1)
                fprintf(stderr, "ERROR in WriteWeights3D: can't open file %s\n",fname);
            if(exitcode==2)
                fprintf(stderr, "ERROR in WriteWeights3D: write to file %s terminated early\n",fname);
            exit(-1);
        }
    }
    return 0;
}

/* Utility for allocating memory for Sino */
/* Returns 0 if no error occurs */
int AllocateSinoData3DParallel(struct Sino3DParallel *sinogram)  /* Input: Sinogram data+parameters structure */
{
    sinogram->sino   = (float **)multialloc(sizeof(float), 2, sinogram->sinoparams.NSlices,sinogram->sinoparams.NViews * sinogram->sinoparams.NChannels);
    sinogram->weight = (float **)multialloc(sizeof(float), 2, sinogram->sinoparams.NSlices,sinogram->sinoparams.NViews * sinogram->sinoparams.NChannels);
    return 0;
}

/* Utility for freeing memory allocated for sinogram, weights and ViewAngles */
/* Returns 0 if no error occurs */
int FreeSinoData3DParallel(struct Sino3DParallel *sinogram)  /* Input: Sinogram data+parameters structure */
{
    multifree(sinogram->sino,2);
    multifree(sinogram->weight,2);
    free((void *)sinogram->sinoparams.ViewAngles);
    return 0;
}


/******************************************/
/*     Image I/O and memory allocation    */
/******************************************/

/* Utility for reading 3D image data */
/* Warning: Memory must be allocated before use */
/* Returns 0 if no error occurs */
int ReadImage3D(
    char *basename,	/* Source base filename, i.e. <basename>_slice<Index>.2Dimgdata for given index range */
    struct Image3D *Image)  /* Image data+params data structure */
{
    char fname[1024];
    int i,Nz,FirstSliceNumber,M,exitcode;
    
    Nz = Image->imgparams.Nz;
    FirstSliceNumber = Image->imgparams.FirstSliceNumber;
    M = Image->imgparams.Nx * Image->imgparams.Ny;
    
    for(i=0;i<Nz;i++)
    {
        sprintf(fname,"%s_slice%.*d.2Dimgdata",basename, Image->imgparams.NumSliceDigits, i+FirstSliceNumber);
        //sprintf(fname,"%s_slice%.*d.2Dimgdata",basename,MBIR_MODULAR_MAX_NUMBER_OF_SLICE_DIGITS,i+FirstSliceNumber);
        //printf("filename: |%s|\n",fname);
        
        if( (exitcode=ReadFloatArray(fname,Image->image[i],M)) ) {
            if(exitcode==1)
                fprintf(stderr, "ERROR in ReadImage3D: can't open file %s\n",fname);
            if(exitcode==2)
                fprintf(stderr, "ERROR in ReadImage3D: read from file %s terminated early\n",fname);
            exit(-1);
        }
    }
    return 0;
}

/* Utility for writing 3D image data */
/* Returns 0 if no error occurs */
int WriteImage3D(
    char *basename,	/* Destination base filename, i.e. <basename>_slice<Index>.2Dimgdata for given index range */
    struct Image3D *Image)  /* Image data+params data structure */
{
    char fname[1024];
    int i,Nz,FirstSliceNumber,M,exitcode;
    
    Nz = Image->imgparams.Nz;
    FirstSliceNumber = Image->imgparams.FirstSliceNumber;
    M = Image->imgparams.Nx * Image->imgparams.Ny;
    
    for(i=0;i<Nz;i++)
    {
        sprintf(fname,"%s_slice%.*d.2Dimgdata",basename, Image->imgparams.NumSliceDigits, i+FirstSliceNumber);
        //sprintf(fname,"%s_slice%.*d.2Dimgdata",basename,MBIR_MODULAR_MAX_NUMBER_OF_SLICE_DIGITS,i+FirstSliceNumber);
        //printf("filename: |%s|\n",fname);
        
        if( (exitcode=WriteFloatArray(fname,Image->image[i],M)) ) {
            if(exitcode==1)
                fprintf(stderr, "ERROR in WriteImage3D: can't open file %s\n",fname);
            if(exitcode==2)
                fprintf(stderr, "ERROR in WriteImage3D: write to file %s terminated early\n",fname);
            exit(-1);
        }
    }
    return 0;
}

/* Utility for allocating memory for Image */
/* Returns 0 if no error occurs */
int AllocateImageData3D(struct Image3D *Image)
{
    Image->image = (float **)multialloc(sizeof(float), 2, Image->imgparams.Nz, Image->imgparams.Nx * Image->imgparams.Ny);
    return 0;
}

/* Utility for freeing memory for Image */
/* Returns 0 if no error occurs */
int FreeImageData3D(struct Image3D *Image)
{
    multifree(Image->image,2);
    return 0;
}



/*********************************************************/
/*    Sparse system matrix I/O and memory allocation     */
/*********************************************************/

/* Utility for reading/allocating the Sparse System Matrix */
/* NOTE: Memory is allocated for the data structure inside subroutine */
/* Returns 0 if no error occurs */
int ReadSysMatrix2D(
    char *fname,	/* Source base filename, i.e. <fname>.2dsysmatrix */
    struct SysMatrix2D *A)  /* Sparse system matrix structure */
{
    FILE *fp;
    int i, Ncolumns, Nnonzero;
    
    strcat(fname,".2Dsysmatrix"); /* append file extension */
    
    /* Allocate memory */
    Ncolumns=A->Ncolumns;
    A->column = (struct SparseColumn *)get_spc(Ncolumns, sizeof(struct SparseColumn));
    
    //printf("\nReading System-matrix ... \n");
    
    if ((fp = fopen(fname, "r")) == NULL)
    {
        fprintf(stderr, "ERROR in ReadSysMatrix2D: can't open file %s.\n", fname);
        exit(-1);
    }
    
    for (i = 0; i < Ncolumns; i++)
    {
        if(fread(&Nnonzero, sizeof(int), 1, fp) != 1)
        {
            fprintf(stderr, "ERROR in ReadSysMatrix2D: file terminated early %s.\n", fname);
            exit(-1);
        }
        A->column[i].Nnonzero = Nnonzero;
        
        if(Nnonzero > 0)
        {
            A->column[i].RowIndex = (int *)get_spc(Nnonzero, sizeof(int));
            A->column[i].Value    = (float *)get_spc(Nnonzero, sizeof(float));
            
            if(fread(A->column[i].RowIndex, sizeof(int), Nnonzero, fp) != (size_t)Nnonzero)
            {
                fprintf(stderr, "ERROR in ReadSysMatrix2D: file terminated early %s.\n", fname);
                exit(-1);
            }
            
            if(fread(A->column[i].Value, sizeof(float), Nnonzero, fp) != (size_t)Nnonzero)
            {
                fprintf(stderr, "ERROR in ReadSysMatrix2D: file terminated early %s.\n", fname);
                exit(-1);
            }
        }
    }
    fclose(fp);
    return 0;
}


/* Utility for writing the Sparse System Matrix */
/* Returns 0 if no error occurs */
int WriteSysMatrix2D(
	char *fname,	/* Destination base filename, i.e. <fname>.2dsysmatrix */
	struct SysMatrix2D *A)  /* Sparse system matrix structure */
{
    FILE *fp;
    int i, Nnonzero, Ncolumns;

    strcat(fname,".2Dsysmatrix"); /* append file extension */
   
    if ((fp = fopen(fname, "w")) == NULL)
    {
        fprintf(stderr, "ERROR in WriteSysMatrix2D: can't open file %s.\n", fname);
        exit(-1);
    }

    Ncolumns = A->Ncolumns;

    for (i = 0; i < Ncolumns; i++)
    {
        Nnonzero = A->column[i].Nnonzero;
        fwrite(&Nnonzero, sizeof(int), 1, fp);

        if(Nnonzero>0)
        {
            fwrite(A->column[i].RowIndex, sizeof(int), Nnonzero, fp);
            fwrite(A->column[i].Value, sizeof(float), Nnonzero, fp);
        }
    }
    fclose(fp);
    return 0;
}

/* Utility for freeing memory from Sparse System Matrix */
/* Returns 0 if no error occurs */
int FreeSysMatrix2D(struct SysMatrix2D *A)
{
    int i;

    for (i = 0; i < (A->Ncolumns); i++)
    {
        free((void *)A->column[i].RowIndex);
        free((void *)A->column[i].Value);
    }
    return 0;
}



/************************************************************/
/*     Strictly 2D sinogram/image memory allocation     */
/************************************************************/

/* Utility for allocating memory for 2D sinogram and weights */
/* Returns 0 if no error occurs */
int AllocateSinoData2DParallel(struct Sino2DParallel *sinogram)
{
    sinogram->sino   = (float *)get_spc(sinogram->sinoparams.NViews * sinogram->sinoparams.NChannels, sizeof(float));
    sinogram->weight = (float *)get_spc(sinogram->sinoparams.NViews * sinogram->sinoparams.NChannels, sizeof(float));
    return 0;
}

/* Utility for freeing 2D sinogram memory including sino, weights and ViewAngles */
/* Returns 0 if no error occurs */
int FreeSinoData2DParallel(struct Sino2DParallel *sinogram)
{
    free((void *)sinogram->sino);
    free((void *)sinogram->weight);
    free((void *)sinogram->sinoparams.ViewAngles);
    return 0;
}

/* Utility for allocating memory for 2D Image */
/* Returns 0 if no error occurs */
int AllocateImageData2D(struct Image2D *Image)
{
    Image->image = (float *)get_spc(Image->imgparams.Nx * Image->imgparams.Ny, sizeof(float));
    return 0;
}

/* Utility for freeing memory for 2D Image */
/* Returns 0 if no error occurs */
int FreeImageData2D(struct Image2D *Image)
{
    free((void *)Image->image);
    return 0;
}


/************************/
/*    Other utilities   */
/************************/

/* Detect the number of slice index digits in given sinogram data file */
/* Returns number of digits, or 0 if no readable files found */
int NumSinoSliceDigits(char *basename, int slice)
{
    FILE *fp;
    char fname[1024];
    int Ndigits = MBIR_MODULAR_MAX_NUMBER_OF_SLICE_DIGITS;

    while(Ndigits > 0)
    {
        sprintf(fname,"%s_slice%.*d.2Dsinodata",basename, Ndigits, slice);
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


/* Compute sinogram weights */
void ComputeSinoWeights(
	struct Sino3DParallel sinogram,
	struct ReconParams reconparams)
{
    int i,j;
    int NSlices = sinogram.sinoparams.NSlices;
    int M = sinogram.sinoparams.NViews * sinogram.sinoparams.NChannels;
    float ** y = sinogram.sino;
    float ** w = sinogram.weight;
    float SigmaYsq = reconparams.SigmaY * reconparams.SigmaY;

    if(reconparams.weightType==0)  // file provided
    {
        for(i=0;i<NSlices;i++)
        for(j=0;j<M;j++)
            w[i][j] /= SigmaYsq;
    }
    else if(reconparams.weightType==1)  // unweighted (uniform)
    {
        for(i=0;i<NSlices;i++)
        for(j=0;j<M;j++)
            w[i][j] = 1.0f/SigmaYsq;
    }
    else if(reconparams.weightType==2)  // transmission
    {
        for(i=0;i<NSlices;i++)
        for(j=0;j<M;j++)
            w[i][j] = expf(-y[i][j])/SigmaYsq;
    }
    else if(reconparams.weightType==3)  // transmission, square root
    {
        for(i=0;i<NSlices;i++)
        for(j=0;j<M;j++)
            w[i][j] = expf(-y[i][j]/2.0f)/SigmaYsq;
    }
    else if(reconparams.weightType==4)  // emission
    {
        for(i=0;i<NSlices;i++)
        for(j=0;j<M;j++)
            w[i][j] = 1.0f/(y[i][j]+0.1f)/SigmaYsq;
    }
    else    // default is unweighted (uniform)
    {
        for(i=0;i<NSlices;i++)
        for(j=0;j<M;j++)
            w[i][j] = 1.0f/SigmaYsq;
    }

}




import numpy as np
import ctypes           # Import python package required to use cython
cimport cython          # Import cython package
cimport numpy as cnp    # Import specialized cython support for numpy

# Import c data structure
cdef extern from "./sv-mbirct/src/MBIRModularDefs.h":
    # 3D Sinogram Parameters 
    struct SinoParams3DParallel:
        int NChannels;         # Number of channels in detector 
        float DeltaChannel;    # Detector spacing (mm) 
        float CenterOffset;    # Offset of center-of-rotation ... 
                               # Computed from center of detector in increasing direction (no. of channels) 
                               # This can be fractional though 
        int NViews;            # Number of view angles 
        float *ViewAngles;     # Array of NTheta view angle entries in degrees 
        int NSlices;           # Number of rows (slices) stored in Sino array 
        float DeltaSlice;      # Spacing along row (slice) direction (mm) 
        int FirstSliceNumber;  # Row (slice) index coresponding to first row (slice) stored in Sino array 
                               # This is in absolute coordinates and is used if a partial set of slices is needed 
        int NumSliceDigits;    # Number of slice numbers digits used in file name 
        
    # 3D Image parameters
    struct ImageParams3D:
        int Nx;                 # Number of columns in image 
        int Ny;                 # Number of rows in image 
        float Deltaxy;          # Spacing between pixels in x and y direction (mm) 
        float ROIRadius;        # Radius of the reconstruction (mm) 
        float DeltaZ;           # Spacing between pixels in z direction (mm) [This should be equal to DeltaSlice 
        int Nz;                 # Number of rows (slices) in image 
        int FirstSliceNumber;   # Detector row (slice) index cooresponding to first row (slice) stored in Image array 
                                # This is in absolute coordinates and is used if a partial set of slices is needed 
        int NumSliceDigits;     # Number of slice numbers digits used in file name

    # Reconstruction Parameters Data Structure
    struct ReconParams:
        char ReconType;         # 1:QGGMRF_3D, 2:PandP
        # General parameters
        float InitImageValue;   # Initial Condition pixel value. In our examples usually chosen as ...
        float StopThreshold;    # Stopping threshold in percent
        int MaxIterations;      # Maximum number of iterations
        char Positivity;        # Positivity constraint: 1=yes, 0=no
        # sinogram weighting
        float SigmaY;           # Scaling constant for sinogram weights (e.g. W=exp(-y)/SigmaY^2 )
        int weightType;         # How to compute weights if internal, 1: uniform, 2: exp(-y); 3: exp(-y/2), 4: 1/(y+0.1)
        # neighbor weights
        float b_nearest;        # Relative nearest neighbor weight [default = 1]
        float b_diag;           # Relative diagonal neighbor weight in (x,y) plane [default = 1/sqrt(2)]
        float b_interslice;     # Relative neighbor weight along z direction [default = 1]
        # QGGMRF
        float p;                # q-GGMRF p parameter
        float q;                # q-GGMRF q parameter (q=2 is typical choice)
        float T;                # q-GGMRF T parameter
        float SigmaX;           # q-GGMRF sigma_x parameter (mm-1)
        # QGGMRF derived parameters
        float pow_sigmaX_p;     # pow(sigmaX,p)
        float pow_sigmaX_q;     # pow(sigmaX,q)
        float pow_T_qmp;        # pow(T,q-p)
        # Proximal map prior for Plug & Play
        float SigmaXsq;         # derived parameter: SigmaX^2
        float *proximalmap;     # ptr to 3D proximal map image; here to carry it to the ICD update


# Import a c function to compute A matrix.
cdef extern from "./sv-mbirct/src/A_comp.h":
    void AmatrixComputeToFile(
        ImageParams3D imgparams,
        SinoParams3DParallel sinoparams,
        char *Amatrix_fname,
        char verboseLevel);

# Import a c function to project a 3D object to sinogram with a computed A matrix.
cdef extern from "./sv-mbirct/src/recon3d.h":
    void forwardProject(
        float *proj,
        float *image,
        ImageParams3D imgparams,
        SinoParams3DParallel sinoparams,
        char *Amatrix_fname,
        char verboseLevel);

    void MBIRReconstruct(
        float *image,
        float *sino,
        float *weight,
        float *proj_init,
        float *proximalmap,
        ImageParams3D imgparams,
        SinoParams3DParallel sinoparams,
        ReconParams reconparams,
        char *Amatrix_fname,
        char verboseLevel);

cdef convert_py2c_ImageParams3D(ImageParams3D* imgparams,
                                py_imageparams):
    imgparams.Nx = py_imageparams['Nx']
    imgparams.Ny = py_imageparams['Ny']
    imgparams.Deltaxy = py_imageparams['Deltaxy']
    imgparams.ROIRadius = py_imageparams['ROIRadius']
    imgparams.DeltaZ = py_imageparams['DeltaZ']
    imgparams.Nz = py_imageparams['Nz']
    imgparams.FirstSliceNumber = py_imageparams['FirstSliceNumber']
    imgparams.NumSliceDigits = py_imageparams['NumSliceDigits']


cdef convert_py2c_SinoParams3D(SinoParams3DParallel* sinoparams,
                        py_sinoparams,
                        float[:] ViewAngles):
    sinoparams.NChannels = py_sinoparams['NChannels']
    sinoparams.DeltaChannel = py_sinoparams['DeltaChannel']
    sinoparams.CenterOffset = py_sinoparams['CenterOffset']
    sinoparams.NViews = py_sinoparams['NViews']
    sinoparams.ViewAngles = &ViewAngles[0] # Assign pointer for float array in C data structure
    sinoparams.NSlices = py_sinoparams['NSlices']
    sinoparams.DeltaSlice = py_sinoparams['DeltaSlice']
    sinoparams.FirstSliceNumber = py_sinoparams['FirstSliceNumber']
    sinoparams.NumSliceDigits = py_sinoparams['NumSliceDigits']


cdef convert_py2c_ReconParams3D(ReconParams* reconparams,
                                py_reconparams):
    reconparams.ReconType = py_reconparams['ReconType']             # 1:QGGMRF_3D, 2:PandP
    # General parameters
    reconparams.InitImageValue = py_reconparams['InitImageValue']   # Initial Condition pixel value. In our examples usually chosen as ...
    reconparams.StopThreshold = py_reconparams['StopThreshold']     # Stopping threshold in percent
    reconparams.MaxIterations = py_reconparams['MaxIterations']     # Maximum number of iterations
    reconparams.Positivity = py_reconparams['Positivity']           # Positivity constraint: 1=yes, 0=no
    # sinogram weighting
    reconparams.SigmaY = py_reconparams['SigmaY']                   # Scaling constant for sinogram weights (e.g. W=exp(-y)/SigmaY^2 )
    reconparams.weightType = py_reconparams['weightType']           # How to compute weights if internal, 1: uniform, 2: exp(-y); 3: exp(-y/2), 4: 1/(y+0.1)
    # neighbor weights
    reconparams.b_nearest = py_reconparams['b_nearest']             # Relative nearest neighbor weight [default = 1]
    reconparams.b_diag = py_reconparams['b_diag']                   # Relative diagonal neighbor weight in (x,y) plane [default = 1/sqrt(2)]
    reconparams.b_interslice = py_reconparams['b_interslice']       # Relative neighbor weight along z direction [default = 1]
    # QGGMRF
    reconparams.p = py_reconparams['p']                             # q-GGMRF p parameter
    reconparams.q = py_reconparams['q']                             # q-GGMRF q parameter (q=2 is typical choice)
    reconparams.T = py_reconparams['T']                             # q-GGMRF T parameter
    reconparams.SigmaX = py_reconparams['SigmaX']                   # q-GGMRF sigma_x parameter (mm-1)
    # QGGMRF derived parameters
    reconparams.pow_sigmaX_p = py_reconparams['pow_sigmaX_p']       # pow(sigmaX,p)
    reconparams.pow_sigmaX_q = py_reconparams['pow_sigmaX_q']       # pow(sigmaX,q)
    reconparams.pow_T_qmp = py_reconparams['pow_T_qmp']             # pow(T,q-p)
    # Proximal map prior for Plug & Play
    reconparams.SigmaXsq = py_reconparams['SigmaXsq']               # derived parameter: SigmaX^2


def cy_AmatrixComputeToFile(py_imageparams,
                            py_sinoparams,
                            char[:] Amatrix_fname,
                            char verboseLevel):
    '''
    Cython wrapper that calls c code to compute A matrix to file.
    Args:
        py_imageparams: python dictionary stores image parameters
        py_sinoparams: python dictionary stores sinogram parameters
        Amatrix_fname: path to store computed A matrix.
        verboseLevel: Possible values are {0,1,2}, where 0 is quiet, 1 prints minimal reconstruction progress information, and 2 prints the full information.

    Returns:

    '''
    # Declare image and sinogram Parameter structures.
    cdef ImageParams3D imgparams
    cdef SinoParams3DParallel sinoparams

    # Convert parameter python dictionaries to c structures based on given py parameter List.
    convert_py2c_ImageParams3D(&imgparams, py_imageparams)
    convert_py2c_SinoParams3D(&sinoparams, py_sinoparams, py_sinoparams['ViewAngles'])

    # Compute A matrix.
    AmatrixComputeToFile(imgparams,sinoparams,&Amatrix_fname[0],verboseLevel)

def cy_forwardProject(cnp.ndarray py_image,
                      py_imageparams,
                      py_sinoparams,
                      char[:] Amatrix_fname,
                      char verboseLevel):
    '''
    Cython wrapper that calls c code to project a 3D image to sinogram.
    Args:
        py_image: 3D numpy float array with a shape of (num_slices,num_row,num_col). The 3D numpy float array should has C continuous order.
        py_imageparams: python dictionary stores image parameters
        py_sinoparams: python dictionary stores sinogram parameters
        Amatrix_fname: path to store computed A matrix.
        verboseLevel: Possible values are {0,1,2}, where 0 is quiet, 1 prints minimal reconstruction progress information, and 2 prints the full information.

    Returns:
        py_proj: 3D numpy float array with a shape of (num_slices,num_views,num_channels) that is the projection from give 3D image.

    '''
    # Get shapes of image and projection
    cdef int nslices = np.shape(py_image)[0]
    cdef int nrows = np.shape(py_image)[1]
    cdef int ncols_img = np.shape(py_image)[2]

    cdef int nviews = py_sinoparams['NViews']
    cdef int nchannels = py_sinoparams['NChannels']


    if not py_image.flags["C_CONTIGUOUS"]:
        raise AttributeError("3D np.ndarrays must be C-contiguous")

    cdef cnp.ndarray[float, ndim=3, mode="c"] cy_image = py_image

    # Allocates memory, without initialization, for matrix to be passed back from C subroutine
    cdef cnp.ndarray[float, ndim=3, mode="c"] py_proj = np.empty((nslices, nviews, nchannels), dtype=ctypes.c_float)

    cdef ImageParams3D imgparams
    cdef SinoParams3DParallel sinoparams

    # Write parameter to c structures based on given py parameter List.
    convert_py2c_ImageParams3D(&imgparams, py_imageparams)
    convert_py2c_SinoParams3D(&sinoparams, py_sinoparams, py_sinoparams['ViewAngles'])

    # Forward projection by calling C subroutine
    forwardProject(&py_proj[0,0,0], &cy_image[0,0,0], imgparams,sinoparams,&Amatrix_fname[0],verboseLevel)

    # Return cython ndarray
    return py_proj


def cy_MBIRReconstruct(cnp.ndarray py_sino,
                       cnp.ndarray py_weight,
                       py_imageparams,
                       py_sinoparams,
                       py_reconparams,
                       char[:] Amatrix_fname,
                       char verboseLevel,
                       cnp.ndarray py_image_init = None,
                       cnp.ndarray py_proj_init = None,
                       cnp.ndarray py_proximalmap = None):
    '''

    Args:

        py_sino: 3D numpy float array with a shape of (num_slices,num_views,num_channels) that is the projection from give 3D image.
        py_weight: 3D numpy float array with a shape of (num_slices,num_views,num_channels)
        py_imageparams: python dictionary stores image parameters
        py_sinoparams: python dictionary stores sinogram parameters
        py_reconparams: python dictionary stores reconstruction parameters
        Amatrix_fname: path to store computed A matrix.
        verboseLevel: Possible values are {0,1,2}, where 0 is quiet, 1 prints minimal reconstruction progress information, and 2 prints the full information.
        py_image_init: 3D numpy float array with a shape of (num_slices,num_row,num_col). The 3D numpy float array should has C continuous order.
        py_proj_init: 3D numpy float array with a shape of (num_slices,num_views,num_channels). The 3D numpy float array should has C continuous order.
        py_proximalmap: 3D numpy float array with a shape of (num_slices,num_row,num_col). The 3D numpy float array should has C continuous order.

    Returns:
        py_image: 3D numpy float array with a shape of (num_slices,num_row,num_col). The 3D numpy float array should has C continuous order.

    '''

    # Get shapes of image and projection
    cdef int nslices = py_imageparams['Nz']
    cdef int nrows = py_imageparams['Ny']
    cdef int ncols = py_imageparams['Nx']

    cdef int nviews = np.shape(py_sino)[1]
    cdef int nchannels = np.shape(py_sino)[2]



    if not py_sino.flags["C_CONTIGUOUS"]:
        raise AttributeError("For py_sino, 3D np.ndarrays must be C-contiguous")

    if not py_weight.flags["C_CONTIGUOUS"]:
        raise AttributeError("For py_weight, 3D np.ndarrays must be C-contiguous")

    cdef cnp.ndarray[float, ndim=3, mode="c"] cy_sino = py_sino
    cdef cnp.ndarray[float, ndim=3, mode="c"] cy_weight = py_weight
    cdef cnp.ndarray[float, ndim=3, mode="c"] cy_proj_init
    cdef cnp.ndarray[float, ndim=3, mode="c"] cy_proximalmap

    if py_image_init is not None:
        if not py_image_init.flags["C_CONTIGUOUS"]:
            raise AttributeError("For py_image_init, 3D np.ndarrays must be C-contiguous")

    if py_proj_init is not None:
        if not py_proj_init.flags["C_CONTIGUOUS"]:
            raise AttributeError("For py_proj_init, 3D np.ndarrays must be C-contiguous")
        cy_proj_init = py_proj_init


    if py_proximalmap is not None:
        if not py_proximalmap.flags["C_CONTIGUOUS"]:
            raise AttributeError("For py_proximalmap, 3D np.ndarrays must be C-contiguous")
        cy_proximalmap = py_proximalmap

    # Allocates memory, without initialization, for matrix to be passed back from C subroutine
    cdef cnp.ndarray[float, ndim=3, mode="c"] py_image
    if py_image_init is not None:
        py_image = np.copy(py_image_init).astype(ctypes.c_float)
    else:
        py_image = np.zeros((nslices, nrows, ncols), dtype=ctypes.c_float)+py_reconparams['InitImageValue']

    cdef ImageParams3D imgparams
    cdef SinoParams3DParallel sinoparams
    cdef ReconParams reconparams

    # Write parameter to c structures based on given py parameter List.
    convert_py2c_ImageParams3D(&imgparams, py_imageparams)
    convert_py2c_SinoParams3D(&sinoparams, py_sinoparams, py_sinoparams['ViewAngles'])
    convert_py2c_ReconParams3D(&reconparams, py_reconparams)

    # Forward projection by calling C subroutine
    MBIRReconstruct(&py_image[0,0,0],
                    &cy_sino[0,0,0],
                    &cy_weight[0,0,0],
                    &cy_proj_init[0,0,0] if py_proj_init is not None else NULL,
                    &cy_proximalmap[0,0,0] if py_proximalmap is not None else NULL,
                    imgparams,
                    sinoparams,
                    reconparams,
                    &Amatrix_fname[0],
                    verboseLevel)

    # Return cython ndarray
    return py_image
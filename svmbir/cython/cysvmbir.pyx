import numpy as np
import ctypes           # Import python package required to use cython
cimport cython          # Import cython package
cimport numpy as cnp    # Import specialized cython support for numpy

# Import c data structure
cdef extern from "../sv-mbirct/src/MBIRModularDefs.h":
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

# Import a c function to compute A matrix.
cdef extern from "../sv-mbirct/src/A_comp.h":
    void AmatrixComputeToFile(
        ImageParams3D imgparams,
        SinoParams3DParallel sinoparams,
        char *Amatrix_fname,
        char verboseLevel);

# Import a c function to project a 3D object to sinogram with a computed A matrix.
cdef extern from "../sv-mbirct/src/recon3d.h":
    void forwardProject(
        float *image,
        float *proj,
        ImageParams3D imgparams,
        SinoParams3DParallel sinoparams,
        char *Amatrix_fname,
        char verboseLevel);

cdef write_ImageParams3D(ImageParams3D* imgparams,
                         py_imageparams):
    imgparams.Nx = py_imageparams['Nx']
    imgparams.Ny = py_imageparams['Ny']
    imgparams.Deltaxy = py_imageparams['Deltaxy']
    imgparams.ROIRadius = py_imageparams['ROIRadius']
    imgparams.DeltaZ = py_imageparams['DeltaZ']
    imgparams.Nz = py_imageparams['Nz']
    imgparams.FirstSliceNumber = py_imageparams['FirstSliceNumber']
    imgparams.NumSliceDigits = py_imageparams['NumSliceDigits']


cdef write_SinoParams3D(SinoParams3DParallel* sinoparams,
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

    # Write parameter to c structures based on given py parameter List.
    write_ImageParams3D(&imgparams, py_imageparams)
    write_SinoParams3D(&sinoparams, py_sinoparams, py_sinoparams['ViewAngles'])

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
    write_ImageParams3D(&imgparams, py_imageparams)
    write_SinoParams3D(&sinoparams, py_sinoparams, py_sinoparams['ViewAngles'])

    # Forward projection by calling C subroutine
    forwardProject(&cy_image[0,0,0], &py_proj[0,0,0], imgparams,sinoparams,&Amatrix_fname[0],verboseLevel)

    # Return cython ndarray
    return py_proj
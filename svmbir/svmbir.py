
import os
import argparse
from glob import glob
import numpy as np
import subprocess
import math
import hashlib

from .utils import *

__exec_path__ = os.path.realpath(os.path.join(os.path.dirname(__file__),'sv-mbirct/bin/mbir_ct'))

__svmbir_lib_path = os.path.join(os.getenv('HOME'), '.cache', 'svmbir_lib')

_default_reconparams = {'prior_model': 'QGGMRF',
    'init_image_value': 0.0001,
    'p': 1.2,
    'q': 2.0,
    'T': 1.0,
    'sigma_x': 0.01,
    'sigma_y': 1,
    'b_nearest': 1.0,
    'b_diag': 0.707,
    'b_interslice': 1.0,
    'stop_threshold': 0.0,
    'max_iterations': 20,
    'Positivity': 1}

_default_sinoparams = {'Geometry': '3DPARALLEL',
    'NChannels': 512,
    'NViews': 288,
    'NSlices': 1,
    'delta_channel': 1,
    'center_offset': 0,
    'delta_slice': 1,
    'first_slice_number': 0,
    'view_angle_list': 'object.ViewAngleList'}

_map_pyconv2camelcase={'prior_model': 'PriorModel',
    'init_image_value': 'InitImageValue',
    'p': 'p',
    'q': 'q',
    'T': 'T',
    'sigma_x': 'SigmaX',
    'sigma_y': 'SigmaY',
    'b_nearest': 'b_nearest',
    'b_diag': 'b_diag',
    'b_interslice': 'b_interslice',
    'stop_threshold': 'StopThreshold',
    'max_iterations': 'MaxIterations',
    'Positivity': 'Positivity',
    'Geometry': 'Geometry',
    'NChannels': 'NChannels',
    'NViews': 'NViews',
    'NSlices': 'NSlices',
    'delta_channel': 'DeltaChannel',
    'center_offset': 'CenterOffset',
    'delta_slice': 'DeltaSlice',
    'first_slice_number': 'FirstSliceNumber',
    'view_angle_list': 'ViewAngleList'}

def _gen_paths(svmbir_lib_path, object_name='object', sysmatrix_name='object'):

    os.makedirs( os.path.join(svmbir_lib_path,'obj'), exist_ok=True)
    os.makedirs( os.path.join(svmbir_lib_path,'sino'), exist_ok=True)
    os.makedirs( os.path.join(svmbir_lib_path,'weight'), exist_ok=True)
    os.makedirs( os.path.join(svmbir_lib_path,'recon'), exist_ok=True)
    os.makedirs( os.path.join(svmbir_lib_path,'init'), exist_ok=True)
    os.makedirs( os.path.join(svmbir_lib_path,'proj'), exist_ok=True)
    os.makedirs( os.path.join(svmbir_lib_path,'sysmatrix'), exist_ok=True)
    os.makedirs( os.path.join(svmbir_lib_path,'par'), exist_ok=True)

    paths = dict()
    paths['sino_name'] = os.path.join(svmbir_lib_path,'sino',object_name)
    paths['wght_name'] = os.path.join(svmbir_lib_path,'weight',object_name)
    paths['recon_name'] = os.path.join(svmbir_lib_path,'recon',object_name)
    paths['init_name'] = os.path.join(svmbir_lib_path,'init',object_name)
    paths['proj_name'] = os.path.join(svmbir_lib_path,'proj',object_name)
    
    paths['sysmatrix_name'] = os.path.join(svmbir_lib_path,'sysmatrix',sysmatrix_name)
    
    paths['param_name'] = os.path.join(svmbir_lib_path,'par',object_name)
    paths['sinoparams_fname'] = paths['param_name']+'.sinoparams'
    paths['imgparams_fname'] = paths['param_name']+'.imgparams'
    paths['reconparams_fname'] = paths['param_name']+'.reconparams'
    paths['view_angle_list_fname'] = paths['param_name']+'.ViewAngleList'

    paths['view_angle_list_name'] = object_name+'.ViewAngleList'

    return paths

def _transform_pyconv2c(**kwargs):
    ckwargs=dict()
    for key in kwargs:
        if key in _map_pyconv2camelcase.keys():
            ckwargs[_map_pyconv2camelcase[key]]=kwargs[key]
        else:
            ckwargs[key]=kwargs[key]
    return ckwargs

def _hash_params(angles, **kwargs):

    relevant_params = dict()
    relevant_params['Nx'] = kwargs['Nx']
    relevant_params['Ny'] = kwargs['Ny']
    relevant_params['Deltaxy'] = kwargs['Deltaxy']
    relevant_params['ROIRadius'] = kwargs['ROIRadius']
    relevant_params['NChannels'] = kwargs['NChannels']
    relevant_params['NViews'] = kwargs['NViews']
    relevant_params['delta_channel'] = kwargs['delta_channel']
    relevant_params['center_offset'] = kwargs['center_offset']

    hash_input = str(relevant_params)+str(np.around(angles, decimals=6) )

    hash_val = hashlib.sha512(hash_input.encode()).hexdigest()

    # print(hash_input)
    # print(hash_val)

    return hash_val, relevant_params


def _cmd_exec(exec_path=__exec_path__, *args, **kwargs):

    arg_list = [exec_path]
    for key in args:
        arg_list.append('-'+key)

    for key,value in kwargs.items():
        arg_list.append('-'+key)
        arg_list.append(value)

    # print(arg_list)
    # os.environ['OMP_NUM_THREADS'] = '20'
    # os.environ['OMP_DYNAMIC'] = 'true'
    subprocess.run(arg_list)


def gen_sysmatrix(param_name, sysmatrix_name):

    if os.path.exists(sysmatrix_name+'.2Dsvmatrix'):
        print('Found system matrix: {}'.format(sysmatrix_name+'.2Dsvmatrix'))
    else:
        _cmd_exec(i=param_name, j=param_name, m=sysmatrix_name)


def init_geometry(angles, NChannels, NViews, NSlices, center_offset=0, img_downsamp=1, num_threads=1, svmbir_lib_path=__svmbir_lib_path, object_name='object'):

    sinoparams = dict(_default_sinoparams)
    sinoparams['NChannels'] = NChannels
    sinoparams['NViews'] = NViews
    sinoparams['NSlices'] = NSlices
    sinoparams['center_offset'] = center_offset
    sinoparams['view_angle_list'] = object_name+'.ViewAngleList'

    imgparams = dict()
    imgparams['Nx'] = math.ceil(sinoparams['NChannels']/img_downsamp)
    imgparams['Ny'] =  math.ceil(sinoparams['NChannels']/img_downsamp)
    imgparams['Nz'] =  sinoparams['NSlices']
    imgparams['first_slice_number'] = 0
    imgparams['Deltaxy'] = sinoparams['NChannels']/imgparams['Nx']
    imgparams['Deltaz'] = 1
    imgparams['ROIRadius'] = sinoparams['NChannels']/2

    hash_val, relevant_params = _hash_params(angles, **{**sinoparams, **imgparams})

    paths = _gen_paths(svmbir_lib_path, object_name=object_name, sysmatrix_name=hash_val)
    sinoparams_c=_transform_pyconv2c(**sinoparams)
    imgparams_c=_transform_pyconv2c(**imgparams)

    write_params(paths['sinoparams_fname'], **sinoparams_c)
    write_params(paths['imgparams_fname'], **imgparams_c)

    with open(paths['view_angle_list_fname'],'w') as fileID:
        for angle in list(angles):
            fileID.write(str(angle)+"\n")

    gen_sysmatrix(paths['param_name'], paths['sysmatrix_name'])

    return paths, sinoparams, imgparams


def project(angles, recon, center_offset=0, img_downsamp=1, num_threads=1, svmbir_lib_path=__svmbir_lib_path, object_name='object', delete_temps=True):

    print('project')

    os.environ['OMP_NUM_THREADS'] = str(num_threads)
    os.environ['OMP_DYNAMIC'] = 'true'

    NViews = len(angles)
    NSlices = recon.shape[0]
    NChannels = recon.shape[1]*img_downsamp

    paths, sinoparams, imgparams = init_geometry(angles, NChannels=NChannels, NViews=NViews, NSlices=NSlices, center_offset=center_offset, img_downsamp=img_downsamp, 
        num_threads=num_threads, svmbir_lib_path=svmbir_lib_path, object_name=object_name)

    write_recon_openmbir(recon, paths['recon_name']+'_slice', '.2Dimgdata')

    _cmd_exec(i=paths['param_name'], j=paths['param_name'], m=paths['sysmatrix_name'],
        f=paths['proj_name'], t=paths['recon_name'])

    proj = read_sino_openmbir(paths['proj_name']+'_slice', '.2Dprojection', 
        sinoparams['NViews'], sinoparams['NSlices'], sinoparams['NChannels'])

    if delete_temps:
        os.remove( paths['sinoparams_fname'] )
        os.remove( paths['imgparams_fname'] )
        os.remove( paths['view_angle_list_fname'] )

        delete_data_openmbir(paths['recon_name']+'_slice', '.2Dimgdata', imgparams['Nz'])
        delete_data_openmbir(paths['proj_name']+'_slice', '.2Dprojection', sinoparams['NSlices'])

    return proj


def recon(angles, sino, wght, center_offset=0, img_downsamp=1, init_recon=None, num_threads=1, svmbir_lib_path=__svmbir_lib_path, object_name='object', delete_temps=True, **recon_kwargs):

    print('recon')

    os.environ['OMP_NUM_THREADS'] = str(num_threads)
    os.environ['OMP_DYNAMIC'] = 'true'
    
    (NViews, NSlices, NChannels) = sino.shape

    paths, sinoparams, imgparams = init_geometry(angles, NChannels=NChannels, NViews=NViews, NSlices=NSlices, center_offset=center_offset, img_downsamp=img_downsamp, 
        num_threads=num_threads, svmbir_lib_path=svmbir_lib_path, object_name=object_name)

    reconparams = parse_params(_default_reconparams, **recon_kwargs)
    reconparams_c=_transform_pyconv2c(**reconparams)
    write_params(paths['reconparams_fname'], **reconparams_c)

    write_sino_openmbir(sino, paths['sino_name']+'_slice', '.2Dsinodata')
    write_sino_openmbir(wght, paths['wght_name']+'_slice', '.2Dweightdata')


    cmd_args = dict(i=paths['param_name'], j=paths['param_name'], k=paths['param_name'], 
    s=paths['sino_name'], w=paths['wght_name'], f=paths['proj_name'],
    r=paths['recon_name'],
    m=paths['sysmatrix_name'])


    if init_recon is not None:
        print('Starting with initial recon')
        write_recon_openmbir(init_recon, paths['init_name']+'_slice', '.2Dimgdata')
        cmd_args['t'] = paths['init_name']

    _cmd_exec(**cmd_args)

    x = read_recon_openmbir(paths['recon_name']+'_slice', '.2Dimgdata', 
        imgparams['Nx'], imgparams['Ny'], imgparams['Nz'])

    if delete_temps:
        os.remove( paths['sinoparams_fname'] )
        os.remove( paths['imgparams_fname'] )
        os.remove( paths['reconparams_fname'] )
        os.remove( paths['view_angle_list_fname'] )

        delete_data_openmbir(paths['recon_name']+'_slice', '.2Dimgdata', imgparams['Nz'])
        delete_data_openmbir(paths['sino_name']+'_slice', '.2Dsinodata', sinoparams['NSlices'])
        delete_data_openmbir(paths['wght_name']+'_slice', '.2Dweightdata', sinoparams['NSlices'])
        delete_data_openmbir(paths['proj_name']+'_slice', '.2Dprojection', sinoparams['NSlices'])


    return x

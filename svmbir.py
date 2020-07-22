
import os
import argparse
from glob import glob
import numpy as np
import subprocess
import math
import hashlib

from utils import *

__exec_path__ = os.path.realpath(os.path.join(os.path.dirname(__file__),'sv-mbirct/bin/mbir_ct'))

__svmbir_lib_path = os.path.join(os.getenv('HOME'), 'svmbir_lib')

_default_reconparams = {'PriorModel': 'QGGMRF',
    'InitImageValue': 0.0001,
    'p': 1.2,
    'q': 2.0,
    'T': 1.0,
    'SigmaX': 0.01,
    'SigmaY': 1,
    'b_nearest': 1.0,
    'b_diag': 0.707,
    'b_interslice': 1.0,
    'StopThreshold': 0.0,
    'MaxIterations': 20,
    'Positivity': 1}

_default_sinoparams = {'Geometry': '3DPARALLEL',
    'NChannels': 512,
    'NViews': 288,
    'NSlices': 1,
    'DeltaChannel': 1,
    'CenterOffset': 0,
    'DeltaSlice': 1,
    'FirstSliceNumber': 0,
    'ViewAngleList': 'object.ViewAngleList'}


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
    paths['ViewAngleList_fname'] = paths['param_name']+'.ViewAngleList'

    paths['ViewAngleList_name'] = object_name+'.ViewAngleList'

    return paths


def _hash_params(angles, **kwargs):

    relevant_params = dict()
    relevant_params['Nx'] = kwargs['Nx']
    relevant_params['Ny'] = kwargs['Ny']
    relevant_params['Deltaxy'] = kwargs['Deltaxy']
    relevant_params['ROIRadius'] = kwargs['ROIRadius']
    relevant_params['NChannels'] = kwargs['NChannels']
    relevant_params['NViews'] = kwargs['NViews']
    relevant_params['DeltaChannel'] = kwargs['DeltaChannel']
    relevant_params['CenterOffset'] = kwargs['CenterOffset']

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


def run_project(svmbir_lib_path, recon=None):

    paths = _gen_paths(svmbir_lib_path)

    if recon is not None:
        write_recon_openmbir(recon, paths['recon_name']+'_slice', '.2Dimgdata')

    _cmd_exec(i=paths['param_name'], j=paths['param_name'], m=paths['sysmatrix_name'],
        f=paths['proj_name'], t=paths['recon_name'])

    sinoparams = read_params(paths['sinoparams_fname'])
    p = read_sino_openmbir(paths['proj_name']+'_slice', '.2Dprojection', 
        sinoparams['NViews'], sinoparams['NSlices'], sinoparams['NChannels'])

    return p


def recon(angles, sino, wght, svmbir_lib_path=__svmbir_lib_path, object_name='object', CenterOffset=0, img_downsamp=1, init_recon=None, **recon_kwargs):

    (NViews, NSlices, NChannels) = sino.shape

    sinoparams = dict(_default_sinoparams)
    sinoparams['NChannels'] = NChannels
    sinoparams['NViews'] = NViews
    sinoparams['NSlices'] = NSlices
    sinoparams['CenterOffset'] = CenterOffset
    sinoparams['ViewAngleList'] = object_name+'.ViewAngleList'

    imgparams = dict()
    imgparams['Nx'] = math.ceil(sinoparams['NChannels']/img_downsamp)
    imgparams['Ny'] =  math.ceil(sinoparams['NChannels']/img_downsamp)
    imgparams['Nz'] =  math.ceil(sinoparams['NSlices']/img_downsamp)
    imgparams['FirstSliceNumber'] = 0
    imgparams['Deltaxy'] = img_downsamp
    imgparams['DeltaZ'] = img_downsamp
    imgparams['ROIRadius'] = sinoparams['NChannels']/2

    hash_val, relevant_params = _hash_params(angles, **{**sinoparams, **imgparams})

    paths = _gen_paths(svmbir_lib_path, object_name=object_name, sysmatrix_name=hash_val)

    write_params(paths['sinoparams_fname'], **sinoparams)
    write_params(paths['imgparams_fname'], **imgparams)

    with open(paths['ViewAngleList_fname'],'w') as fileID:
        for angle in list(angles):
            fileID.write(str(angle)+"\n")

    _cmd_exec(i=paths['param_name'], j=paths['param_name'], m=paths['sysmatrix_name'])

    reconparams = parse_params(_default_reconparams, **recon_kwargs)
    write_params(paths['reconparams_fname'], **reconparams)

    write_sino_openmbir(sino, paths['sino_name']+'_slice', '.2Dsinodata')
    write_sino_openmbir(wght, paths['wght_name']+'_slice', '.2Dweightdata')

    if init_recon is not None:
        write_recon_openmbir(init_recon, paths['init_name']+'_slice', '.2Dimgdata')

        print('Starting with initial recon')

        _cmd_exec(i=paths['param_name'], j=paths['param_name'], k=paths['param_name'], 
            s=paths['sino_name'], w=paths['wght_name'], f=paths['proj_name'],
            r=paths['recon_name'], t=paths['init_name'],
            m=paths['sysmatrix_name'])

    else:

        _cmd_exec(i=paths['param_name'], j=paths['param_name'], k=paths['param_name'], 
            s=paths['sino_name'], w=paths['wght_name'], f=paths['proj_name'],
            r=paths['recon_name'],
            m=paths['sysmatrix_name'])

    x = read_recon_openmbir(paths['recon_name']+'_slice', '.2Dimgdata', 
        imgparams['Nx'], imgparams['Ny'], imgparams['Nz'])


    return x


import os
import argparse
from glob import glob
import numpy as np
import subprocess
import math

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


def _gen_paths(svmbir_lib_path, object_name='object'):

    paths = dict()
    paths['sino_name'] = os.path.join(svmbir_lib_path,'sino',object_name)
    paths['wght_name'] = os.path.join(svmbir_lib_path,'weight',object_name)
    paths['recon_name'] = os.path.join(svmbir_lib_path,'recon',object_name)
    paths['init_name'] = os.path.join(svmbir_lib_path,'init',object_name)
    paths['proj_name'] = os.path.join(svmbir_lib_path,'proj',object_name)
    paths['sysmatrix_name'] = os.path.join(svmbir_lib_path,'sysmatrix',object_name)
    
    paths['param_name'] = os.path.join(svmbir_lib_path,'par',object_name)
    paths['sinoparams_fname'] = paths['param_name']+'.sinoparams'
    paths['imgparams_fname'] = paths['param_name']+'.imgparams'
    paths['reconparams_fname'] = paths['param_name']+'.reconparams'
    paths['ViewAngleList_fname'] = paths['param_name']+'.ViewAngleList'

    paths['ViewAngleList_name'] = object_name+'.ViewAngleList'

    return paths


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


def gen_sysmatrix(svmbir_lib_path, angles, img_downsamp=1, **sino_kwargs):

    paths = _gen_paths(svmbir_lib_path)
    if not os.path.exists(os.path.dirname(paths['param_name'])):
        os.makedirs(os.path.dirname(paths['param_name']), exist_ok=True)

    # sinoparams_req_keys = ['NChannels', 'NViews', 'NSlices', 'CenterOffset']
    # assert all(key in sinoparams.keys() for key in sinoparams_req_keys), 'required keys ({}) not present'.format(sinoparams_req_keys)

    sinoparams = dict(_default_sinoparams)
    for key in sino_kwargs.keys():
        sinoparams[key] = sino_kwargs[key]
    sinoparams['ViewAngleList'] = paths['ViewAngleList_name']

    imgparams = dict()
    imgparams['Nx'] = math.ceil(sinoparams['NChannels']/img_downsamp)
    imgparams['Ny'] =  math.ceil(sinoparams['NChannels']/img_downsamp)
    imgparams['Nz'] =  math.ceil(sinoparams['NSlices']/img_downsamp)
    imgparams['FirstSliceNumber'] = 0
    imgparams['Deltaxy'] = img_downsamp
    imgparams['DeltaZ'] = img_downsamp
    imgparams['ROIRadius'] = sinoparams['NChannels']/2

    write_params(paths['sinoparams_fname'], **sinoparams)
    write_params(paths['imgparams_fname'], **imgparams)

    with open(paths['ViewAngleList_fname'],'w') as fileID:
        for angle in list(angles):
            fileID.write(str(angle)+"\n")


    if not os.path.exists(os.path.dirname(paths['sysmatrix_name'])):
        os.makedirs(os.path.dirname(paths['sysmatrix_name']), exist_ok=True)

    _cmd_exec(i=paths['param_name'], j=paths['param_name'], m=paths['sysmatrix_name'])    


def run_recon(svmbir_lib_path, sino=None, wght=None, init_recon=None, **recon_kwargs):

    # sino shape: NViews, NSlices, NChannels

    paths = _gen_paths(svmbir_lib_path)

    if not os.path.exists(os.path.dirname(paths['recon_name'])):
        os.makedirs(os.path.dirname(paths['recon_name']), exist_ok=True)

    if not os.path.exists(os.path.dirname(paths['init_name'])):
        os.makedirs(os.path.dirname(paths['init_name']), exist_ok=True)

    if not os.path.exists(os.path.dirname(paths['proj_name'])):
        os.makedirs(os.path.dirname(paths['proj_name']), exist_ok=True)

    if not os.path.exists(os.path.dirname(paths['sino_name'])):
        os.makedirs(os.path.dirname(paths['sino_name']), exist_ok=True)

    if not os.path.exists(os.path.dirname(paths['wght_name'])):
        os.makedirs(os.path.dirname(paths['wght_name']), exist_ok=True)

    reconparams = dict(_default_reconparams)
    for key in recon_kwargs.keys():
        reconparams[key] = recon_kwargs[key]
    write_params(paths['reconparams_fname'], **reconparams)
    
    if sino is not None:
        write_sino_openmbir(sino, paths['sino_name']+'_slice', '.2Dsinodata')
    if wght is not None:
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

    imgparams = read_params(paths['imgparams_fname'])
    x = read_recon_openmbir(paths['recon_name']+'_slice', '.2Dimgdata', 
        imgparams['Nx'], imgparams['Ny'], imgparams['Nz'])

    return x


def run_project(svmbir_lib_path, recon=None):

    paths = _gen_paths(svmbir_lib_path)

    if not os.path.exists(os.path.dirname(paths['proj_name'])):
        os.makedirs(os.path.dirname(paths['proj_name']), exist_ok=True)

    if not os.path.exists(os.path.dirname(paths['recon_name'])):
        os.makedirs(os.path.dirname(paths['recon_name']), exist_ok=True)


    if recon is not None:
        write_recon_openmbir(recon, paths['recon_name']+'_slice', '.2Dimgdata')

    _cmd_exec(i=paths['param_name'], j=paths['param_name'], m=paths['sysmatrix_name'],
        f=paths['proj_name'], t=paths['recon_name'])

    sinoparams = read_params(paths['sinoparams_fname'])
    p = read_sino_openmbir(paths['proj_name']+'_slice', '.2Dprojection', 
        sinoparams['NViews'], sinoparams['NSlices'], sinoparams['NChannels'])

    return p

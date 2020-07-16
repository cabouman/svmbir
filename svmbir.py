
import os
import argparse
from glob import glob
import numpy as np
import subprocess

from utils import *

# from multiprocessing import Pool
# import matplotlib.pyplot as plt

__exec_path__ = os.path.realpath(os.path.join(os.path.dirname(__file__),'sv-mbirct/bin/mbir_ct'))

def cmd_exec(exec_path=__exec_path__, *args, **kwargs):

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


def gen_paths(mbir_data_path, mbir_params_path, object_name):

    paths = dict()

    paths['param_name'] = os.path.join(mbir_params_path,object_name)
    paths['sino_name'] = os.path.join(mbir_data_path,'sino',object_name)
    paths['wght_name'] = os.path.join(mbir_data_path,'weight',object_name)
    paths['recon_name'] = os.path.join(mbir_data_path,'recon',object_name)
    paths['init_name'] = os.path.join(mbir_data_path,'init',object_name)
    paths['proj_name'] = os.path.join(mbir_data_path,'proj',object_name)
    paths['sysmatrix_name'] = os.path.join(mbir_data_path,'sysmatrix',object_name)

    return paths


def init_geometry_data(mbir_data_path, mbir_params_path, object_name, angles, img_downsamp=1, **sinoparams):

    paths = gen_paths(mbir_data_path, mbir_params_path, object_name)

    sinoparams_req_keys = ['NChannels', 'NViews', 'NSlices', 'CenterOffset']

    assert all(key in sinoparams.keys() for key in sinoparams_req_keys), 'required keys ({}) not present'.format(sinoparams_req_keys)

    sinoparams['FirstSliceNumber'] = 0
    sinoparams['DeltaChannel'] = 1
    sinoparams['DeltaSlice'] = 1

    modify_params(paths['param_name']+'.sinoparams', **sinoparams)

    imgparams = dict()
    imgparams['Nx'] = sinoparams['NChannels']//img_downsamp
    imgparams['Ny'] = sinoparams['NChannels']//img_downsamp
    imgparams['Nz'] = sinoparams['NSlices']
    imgparams['FirstSliceNumber'] = 0
    imgparams['Deltaxy'] = img_downsamp
    imgparams['DeltaZ'] = img_downsamp
    imgparams['ROIRadius'] = sinoparams['NChannels']/2

    modify_params(paths['param_name']+'.imgparams', **imgparams)

    ViewAngleList_fname = paths['param_name']+'.ViewAngleList'
    with open(ViewAngleList_fname,'w') as fileID:
        for angle in list(angles):
            fileID.write(str(angle)+"\n")


def modify_img_params(mbir_data_path, mbir_params_path, object_name, **imgparams):

    paths = gen_paths(mbir_data_path, mbir_params_path, object_name)

    modify_params(paths['param_name']+'.imgparams', **imgparams)


def gen_sysmatrix(mbir_data_path, mbir_params_path, object_name):

    paths = gen_paths(mbir_data_path, mbir_params_path, object_name)

    if not os.path.exists(os.path.dirname(paths['sysmatrix_name'])):
        os.makedirs(os.path.dirname(paths['sysmatrix_name']), exist_ok=True)

    cmd_exec(i=paths['param_name'], j=paths['param_name'], m=paths['sysmatrix_name'])


def recon(mbir_data_path, mbir_params_path, object_name, sino=None, wght=None, init_recon=None, **reconparams):

    paths = gen_paths(mbir_data_path, mbir_params_path, object_name)

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

    modify_params(paths['param_name']+'.reconparams', **reconparams)
    
    if sino is not None:
        write_sino_openmbir(sino, paths['sino_name']+'_slice', '.2Dsinodata')
    if wght is not None:
        write_sino_openmbir(wght, paths['wght_name']+'_slice', '.2Dweightdata')
    
    if init_recon is not None:
        write_recon_openmbir(init_recon, paths['init_name']+'_slice', '.2Dimgdata')

        print('Starting with initial recon')

        cmd_exec(i=paths['param_name'], j=paths['param_name'], k=paths['param_name'], 
            s=paths['sino_name'], w=paths['wght_name'], f=paths['proj_name'],
            r=paths['recon_name'], t=paths['init_name'],
            m=paths['sysmatrix_name'])

    else:

        cmd_exec(i=paths['param_name'], j=paths['param_name'], k=paths['param_name'], 
            s=paths['sino_name'], w=paths['wght_name'], f=paths['proj_name'],
            r=paths['recon_name'],
            m=paths['sysmatrix_name'])

    imgparams = read_params(paths['param_name']+'.imgparams')
    x = read_recon_openmbir(paths['recon_name']+'_slice', '.2Dimgdata', 
        imgparams['Nx'], imgparams['Ny'], imgparams['Nz'])

    return x


def project(mbir_data_path, mbir_params_path, object_name, recon=None):

    paths = gen_paths(mbir_data_path, mbir_params_path, object_name)

    if not os.path.exists(os.path.dirname(paths['proj_name'])):
        os.makedirs(os.path.dirname(paths['proj_name']), exist_ok=True)

    if not os.path.exists(os.path.dirname(paths['recon_name'])):
        os.makedirs(os.path.dirname(paths['recon_name']), exist_ok=True)


    if recon is not None:
        write_recon_openmbir(recon, paths['recon_name']+'_slice', '.2Dimgdata')

    cmd_exec(i=paths['param_name'], j=paths['param_name'], m=paths['sysmatrix_name'],
        f=paths['proj_name'], t=paths['recon_name'])

    sinoparams = read_params(paths['param_name']+'.sinoparams')
    p = read_sino_openmbir(paths['proj_name']+'_slice', '.2Dprojection', 
        sinoparams['NViews'], sinoparams['NSlices'], sinoparams['NChannels'])

    return p

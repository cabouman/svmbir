# -*- coding: utf-8 -*-
# Copyright (C) by
# All rights reserved.

import svmbir
import svmbir._utils as utils
import numpy as np
import yaml
from inspect import signature


class ParallelBeamCT:
    """ Class that wraps svmbir.recon() and related functions.
    Args:
        keyword arguments for svmbir.recon(), svmbir.project(), svmbir.backproject()
    Attributes:
        params (dict): Dictionary of key-worded arguments
    Returns:
        None
    Todo:
        mask = par_ct.return_mask()
    """

    def __init__(self, **kwargs):
        self.params = dict()
        self.reset_to_default()
        self.update_args(self.params, **kwargs)

    def _make_temp_args(self, function, **kwargs):
        temp_params = self.params.copy()
        self.update_args(temp_params, **kwargs)
        # Determine which keyword arguments are allowed for this function
        sig = str(signature(function))
        args = sig[1:-1].split(', ')  # Separate the signature string into components like 'num_rows' or 'num_rows=None'
        kwargs = [arg for arg in args if '=' in arg]  # Get the components with '=' to signify keyword argument
        keys = [arg.split('=')[0] for arg in kwargs]  # Split each argument at the '=' and take the first part
        # Delete the unneeded keys
        for key in set(temp_params.keys()):
            if key not in keys:
                temp_params.pop(key)
        return temp_params

    def recon(self, sino, angles, **kwargs):
        temp_params = self._make_temp_args(svmbir.recon, **kwargs)
        return svmbir.recon(sino, angles, **temp_params)

    def project(self, image, angles, num_channels, **kwargs):
        temp_params = self._make_temp_args(svmbir.project, **kwargs)
        return svmbir.project(image, angles, num_channels, **temp_params)

    def backproject(self, sino, angles, **kwargs):
        temp_params = self._make_temp_args(svmbir.backproject, **kwargs)
        return svmbir.backproject(sino, angles, **temp_params)

    # Todo
    def return_mask(self):
        print("in return_mask()..TBD")

    def reset_to_default(self):
        """Set instance params dictionary to defaults"""
        self.params = utils.recon_defaults_dict.copy()

    @staticmethod
    def get_defaults():
        """Get instance params dictionary to defaults"""
        return utils.recon_defaults_dict.copy()

    def set_params(self, **kwargs):
        """Set multiple keys in instance params dict."""
        self.update_args(self.params, **kwargs)

    def print_params(self):
        print("----")
        for key, val in self.params.items():
            print("{} = {}".format(key, val))

    def save_params(self, fname='param_dict.npy', binaries=False):
        """Save parameter dict to numpy/pickle file/yaml file"""
        output_params = self.params.copy()
        if binaries is False:
            # Wipe the binaries before saving.
            output_params['weights'] = None
            output_params['prox_image'] = None
            output_params['init_proj'] = None
            if not np.isscalar(output_params['init_image']):
                output_params['init_image'] = None
        # Determine file type
        if fname[-4:] == '.npy':
            np.save(fname, output_params)
        elif fname[-4:] == '.yml' or fname[-5:] == '.yaml':
            # Work through all the parameters by group, with a heading for each group
            with open(fname, 'w') as file:
                for heading, dic in zip(ParallelBeamCT.headings, ParallelBeamCT.dicts):
                    file.write('# ' + heading + '\n')
                    for key in dic.keys():
                        val = self.params[key]
                        file.write(key + ': ' + str(val) + '\n')
        else:
            raise ValueError('Invalid file type for saving parameters: ' + fname)

    def load_params(self, fname):
        """Load parameter dict from numpy/pickle file/yaml file, and merge into instance params"""
        # Determine file type
        if fname[-4:] == '.npy':
            read_dict = np.load(fname, allow_pickle=True).item()
            self.reset_to_default()
            self.update_args(self.params, **read_dict)
        elif fname[-4:] == '.yml' or fname[-5:] == '.yaml':
            with open(fname) as file:
                try:
                    params = yaml.safe_load(file)
                    self.reset_to_default()
                    self.update_args(self.params, **params)
                except yaml.YAMLError as exc:
                    print(exc)

    @staticmethod
    def update_args(params, **kwargs):
        """
        Update parameter dictionary with kwargs input.
        Raises an exception if kwargs key is not defined in dictionary.
        Also performs parameter checking.
        """
        for key, val in kwargs.items():
            if key in params.keys():
                params[key] = val
            else:
                raise NameError('"{}" not a recognized argument'.format(key))
        # Check validity of new parameters
        # Loop through keywords in each of the dicts and call the appropriate test
        for d, test_fcn in zip(utils.dicts, utils.tests):
            cur_dict = d.copy()
            for key in cur_dict.keys():
                cur_dict[key] = params[key]

            # Call the test, which gives a new dictionary, then copy the values
            new_dict = utils.test_args_dict(d, test_fcn, **cur_dict)
            for key in d.keys():
                params[key] = new_dict[key]


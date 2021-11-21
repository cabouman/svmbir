import numpy as np
import matplotlib.pyplot as plt
import svmbir
import os


svmbir_lib_path = 'foo'




num_slices = 1
num_rows = num_cols = 32
num_views = 24
num_channels = 256

x = np.ones((num_slices, num_rows, num_cols))
angles = np.linspace(-np.pi/2, np.pi, num_views, endpoint=False)




class Options():


    def __init__(self, **kwargs):
        self._data = dict(**kwargs)
        self.check_params()

    def dict_repr(self, d):
        return '{' + ', \n'.join('%s: %r' % i for i in d.items()) + '}'

    def __repr__(self):
        with np.printoptions(precision=2):
            return f"{type(self)}\n"\
                   f"data: {self.dict_repr(self._data)}\n"

    def get(self, key):
        return self._data.get(key)

    def getall(self):
        return self._data.copy()

    def copy(self):
        return self.__class__(**self._data)

    def update(self, **kwargs):
        diff = set(kwargs.keys()) - set(self._data.keys())
        if diff:
                raise NameError(f'Unrecognized arguments: {diff}')
        self._data.update(**kwargs)
        self.check_params()

    def check_params(self):
        print('Checking whether Options make sense ...')

opt = Options(a=1, b='two')
opt.get('a')
opt.getall()
o2 = opt.copy()
opt.update(a=11)
opt

# opt.update(c=3)


class ProjectorOptions(Options):

    def __init__(   self,
                    angles,
                    num_slices,
                    num_channels,
                    num_rows=None,
                    num_cols=None,
                    roi_radius=None,
                    delta_channel=1.0,
                    delta_pixel=1.0,
                    center_offset=0.0,
                    svmbir_lib_path=svmbir_lib_path,
                    object_name='object',
                    delete_temps=True,
                    num_threads=None,
                    verbose=True,
                    ):

        # TODO: check params ...
        self._data = {}
        self._data['angles'] = angles
        self._data['num_slices'] = num_slices
        self._data['num_channels'] = num_channels
        self._data['num_rows'] = num_rows
        self._data['num_cols'] = num_cols
        self._data['roi_radius'] = roi_radius
        self._data['delta_channel'] = delta_channel
        self._data['delta_pixel'] = delta_pixel
        self._data['center_offset'] = center_offset
        self._data['svmbir_lib_path'] = svmbir_lib_path
        self._data['object_name'] = object_name
        self._data['delete_temps'] = delete_temps
        self._data['num_threads'] = num_threads
        self._data['verbose'] = verbose

        self.check_params()

    def check_params(self):
        print('Checking whether ProjectorOptions make sense ...')


projector_opt = ProjectorOptions(angles, num_slices, num_channels, num_cols=num_cols, num_rows=num_rows)
projector_opt2 = projector_opt.copy()

projector_opt2.update(num_slices=projector_opt.get('num_slices')*2) # proper way to update params
assert projector_opt.get('num_slices') != projector_opt2.get('num_slices')

d = projector_opt.getall() # read-only
d['num_slices'] *= 2 # does not change orininal
assert projector_opt.get('num_slices') != d['num_slices']


class Projector():

    def __init__(   self,
                    projector_opt,
                    ):

        self._projector_opt = projector_opt.copy() # .copy() important so that read-only unless using setter routine

        self.input_shape = (self._projector_opt.get('num_slices'),
            self._projector_opt.get('num_rows'), 
            self._projector_opt.get('num_cols'))

        num_views = self._projector_opt.get('angles').size
        self.output_shape = (num_views,
            self._projector_opt.get('num_slices'), 
            self._projector_opt.get('num_channels'))

    def __repr__(self):
        return f"{type(self)}\n"\
               f"input_shape: {self.input_shape}   (num_slices, num_rows, num_cols)\n"\
               f"output_shape: {self.output_shape}   (num_views, num_slices, num_channels)\n"\
               f"projector_opt: {self._projector_opt}\n"\

    def project(self, x):
        print(f'Projecting from {self.input_shape} to {self.output_shape} ...')
        return np.ones(self.output_shape)

    def backproject(self, y):
        print(f'Backprojecting from {self.output_shape} to {self.input_shape} ...')
        return np.ones(self.input_shape)

    def get_projector_options(self):
        return self._projector_opt.getall()

    def update_options(self, **kwargs):
        self._projector_opt.update(**kwargs)




A = Projector(projector_opt)
A.get_projector_options()

y = A.project(x)
ATy = A.backproject(y)

A.update_options(center_offset=0.5)


class LossOptions(Options):

    def __init__(   self,
                    sigma_y=None,
                    sigma_p=1.0,
                    sigma_x=None,
                    p=1.2,
                    q=2.0,
                    T=1.0,
                    b_interslice=1.0,
                    positivity=True,
                    max_resolutions=0,
                    stop_threshold=0.02,
                    max_iterations=100,
                    num_threads=None,
                    verbose=True,
                    ):
        # TODO: check params ...
        self._data = {}
        self._data['sigma_y'] = sigma_y
        self._data['sigma_p'] = sigma_p
        self._data['sigma_x'] = sigma_x
        self._data['p'] = p
        self._data['q'] = q
        self._data['T'] = T
        self._data['b_interslice'] = b_interslice
        self._data['positivity'] = positivity
        self._data['max_resolutions'] = sigma_y
        self._data['stop_threshold'] = sigma_p
        self._data['max_iterations'] = sigma_x
        self._data['num_threads'] = num_threads
        self._data['verbose'] = verbose

        self.check_params()

    def check_params(self):
        print('Checking whether LossOptions make sense ...')



def weight_aux(y, A, weight_type='unweighted', snr_db=30.0, sharpness=0.0):
    return np.ones_like(y), 1, 1

W, sigma_y, sigma_x = weight_aux(y, A, weight_type=None, snr_db=30.0, sharpness=0.0)


loss_opt = LossOptions(sigma_y=sigma_y, sigma_x=sigma_x, p=1.1) # warn if sigmas not set




class Loss():

    def __init__(   self,
                    y,
                    A,
                    W = None,
                    loss_opt=None,
                    it_opt=None
                ):

        # TODO: all kinds of checks
        
        self._y = y
        self._A = A
        self._W = W
        self._loss_opt = loss_opt.copy() # .copy() important so that read-only unless using setter routine

    def __repr__(self):
        with np.printoptions(precision=2):
            return f"{type(self)}\n"\
                   f"y: {type(self._y)} size {self._y.shape}\n\n"\
                   f"A: {type(self._A)} {self._A}\n"\
                   f"W: {type(self._W)} size {self._W.shape}\n\n"\
                   f"loss_opt: {type(self._loss_opt)} {self._loss_opt}\n"\


    def recon(self, init_image=None):
        print('Reconstructing ...')
        if init_image is None:
            init_image = np.zeros(self._A.input_shape)
            print("Initializing with zero ...")
        print(f"init_image: {type(init_image)} size {init_image.shape}\n\n")
        return init_image


    def prox(self, v, λ, init_image=None):
        print(f'Proxxing with λ = {λ} = 1/{1/λ:.5f} = 1/sigma_p')
        if init_image is None:
            init_image = np.zeros(self._A.input_shape)
            print("Initializing with zero ...")
        print(f"init_image: {type(init_image)} size {init_image.shape}\n\n")
        return init_image

    def update_loss(self, **kwargs):
        self._loss_opt.update(**kwargs)

    def update_projector(self, **kwargs):
        self._A.update_options(**kwargs)


A.update_options(center_offset=0.0)
loss_opt.update(p=1.1)

f = Loss(y, A, W=W, loss_opt=loss_opt)

f.update_loss(p=2)
f.update_projector(center_offset=1.0)





# --- Reconstruction

x = f.recon()
# same as
x = f.recon(init_image=np.ones_like(x))


λ = 3.141592
v = np.random.randn(*A.input_shape)

x = f.prox(v, λ)
x = f.prox(v, λ, init_image=v)













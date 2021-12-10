import numpy as np

svmbir_lib_path = 'foo'



num_slices = 1
num_rows = num_cols = 32
num_views = 24
num_channels = 256

x = np.ones((num_slices, num_rows, num_cols))
angles = np.linspace(-np.pi/2, np.pi, num_views, endpoint=False)




class Options():

    """Generic Options Class
    """
    
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

    def get_dict(self):
        return self._data

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

    def save_options(self, file_name):
        # could be useful
        pass






opt = Options(a=1, b='two')
opt.get('a')
opt.get_dict()
o2 = opt.copy()
opt.update(a=11)
# opt.update(a=11, c=22, d=44)







class ProjectorOptions(Options):

    """Options Class for Projector
    """
    
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
        self._data['delete_temps'] = delete_temps # this should be separate somewhere. 
        self._data['num_threads'] = num_threads
        self._data['verbose'] = verbose

        self.check_params()

    def check_params(self):
        print('Checking whether ProjectorOptions make sense ...')






projector_opt = ProjectorOptions(angles, num_slices, num_channels, num_cols=num_cols, num_rows=num_rows)
projector_opt2 = projector_opt.copy()

projector_opt2.update(num_slices=num_slices*100) # proper way to update params
assert projector_opt.get('num_slices') != projector_opt2.get('num_slices')






class Projector():

    """This is the A-matrix
    
    Attributes:
        input_shape (TYPE): Description
        output_shape (TYPE): Description
    """
    
    def __init__(   self,
                    projector_opt,
                    ):

        self._projector_opt = projector_opt

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

    def get_projector_opt(self):
        return self._projector_opt.get_dict()

    def update_options(self, **kwargs):
        self._projector_opt.update(**kwargs)




A = Projector(projector_opt)
A.get_projector_opt()

y = A.project(x)
ATy = A.backproject(y)

A.update_options(center_offset=0.5)






class LossOptions(Options):

    """Options Class for Loss

        Defining parameters in 

            1/(2 σ_y^2) || Ax - y ||_W^2 + (2 σ_p^2) (r_mrf(x) or ||x - x_||^2)

    """
    
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




loss_opt = LossOptions(sigma_y=2.0, sigma_x=2.0, p=1.1) # warn if sigmas not set




class Loss():

    """Class for Loss

        Defining everything in 

            1/(2 σ_y^2) || Ax - y ||_W^2 + (2 σ_p^2) (r_mrf(x) or ||x - x_||^2)

        and allowing optimization of that loss.
    
    Attributes:
        A (TYPE): Description
        loss_opt (TYPE): Description
        W (TYPE): Description
        y (TYPE): Description
    """
    
    def __init__(   self,
                    y,
                    A,
                    W = None,
                    loss_opt=None,
                    it_opt=None
                ):

        
        self.y = y
        self.A = A
        if W is None:
            self.W = np.ones_like(y)
        else:
            self.W = W
        self.loss_opt = loss_opt
        self.check_params()

    def __repr__(self):
        with np.printoptions(precision=2):
            return f"{type(self)}\n"\
                   f"y: {type(self.y)} size {self.y.shape}\n\n"\
                   f"A: {type(self.A)} {self.A}\n"\
                   f"W: {type(self.W)} size {self.W.shape}\n\n"\
                   f"loss_opt: {type(self.loss_opt)} {self.loss_opt}\n"\


    def recon(self, init_image=None):
        print('Reconstructing ...')
        if init_image is None:
            init_image = np.zeros(self.A.input_shape)
            print("Initializing with zero ...")
        print(f"init_image: {type(init_image)} size {init_image.shape}\n\n")
        return init_image


    def prox(self, v, sigma_p=None, init_image=None):
        if sigma_p is None:
            sigma_p = self.sigma_p
        print(f'Proxxing with sigma_p = {sigma_p}')
        if init_image is None:
            init_image = np.zeros(self.A.input_shape)
            print("Initializing with zero ...")
        print(f"init_image: {type(init_image)} size {init_image.shape}\n\n")
        return init_image

    def update_options(self, **kwargs):
        self.loss_opt.update(**kwargs)
        self.check_params()

    def update_projector(self, **kwargs):
        self.A.update_options(**kwargs)
        self.check_params()

    def auto_weighting(self, weight_type='unweighted', snr_db=30.0, sharpness=0.0):
        # weight_type, snr_db, sharpness are not loss_options, they are rather meta options
        # that determine the loss options W, sigma_y, sigma_x.
        W = np.exp(-self.y) # or whatever
        sigma_y = 3.141 # or whatever
        sigma_x = 2.718 # or whatever

        self.W = W
        self.loss_opt.update(sigma_y=sigma_y, sigma_x=sigma_x)
        return W, sigma_y, sigma_x

    def check_params(self):
        # used at init or when params updated
        # Stuff like:
        if self.A.output_shape != self.y.shape:
            raise ValueError(f"Incompatible shapes {self.A.output_shape=}, {self.y.shape=} ")




f = Loss(y, A, W=None, loss_opt=loss_opt)

# # Check Params
# y2 = y[::2]
# f = Loss(y2, A, W=None, loss_opt=loss_opt)



A.update_options(center_offset=0.0)
loss_opt.update(p=1.1)

f = Loss(y, A, W=None, loss_opt=loss_opt)

f.update_options(p=2)
f.update_projector(center_offset=1.0)





# --- Reconstruction

x = f.recon()
x = f.recon(init_image=np.ones_like(x))


sigma_p = 3.141592
v = np.random.randn(*A.input_shape)

x = f.prox(v, sigma_p)
x = f.prox(v, sigma_p, init_image=v)


f.auto_weighting(weight_type=None, snr_db=30.0, sharpness=0.0)
# or if desired
W, sigma_y, sigma_x = f.auto_weighting(weight_type=None, snr_db=30.0, sharpness=0.0)









# --- Functional interface: Wrapped around oo-interface ---
# --- (This seems silly but if we insist on the functional interface ...) ---

# --- CONCEPT ONLY ---
def recon(args, kwargs):
    def opt_parse_recon(args, **kwargs):
        # convertes options from functional interface to oo-interface options
        pass
    projector_opt, loss_opt, y, W, init_image, prox_image = opt_parse_recon(args, kwargs)
    A = Projector(projector_opt)
    f = Loss(y, A, W=W, loss_opt=loss_opt)

    if prox_image:
        # uses sigma_p = f.loss_opt.get('sigma_p')
        return f.prox(prox_image, init_image=init_image)
    else:
        return f.recon(init_image=init_image)

# x = recon(y, angles, ...)



# --- CONCEPT ONLY ---
def project(args, kwargs):
    def opt_parse_project(args, **kwargs):
        # convertes options from functional interface to oo-interface options
        pass
    projector_opt, image = opt_parse_project(args, kwargs)
    A = Projector(projector_opt)
    return A.project(image)

# y = project(x, angles, num_channels, ...)



# --- CONCEPT ONLY ---
def backproject(args, kwargs):
    def opt_parse_backproject(args, **kwargs):
        # convertes options from functional interface to oo-interface options
        pass
    projector_opt, sino = opt_parse_backproject(args, kwargs)
    A = Projector(projector_opt)
    return A.backproject(sino)

# x = backproject(sino, angles, ...)





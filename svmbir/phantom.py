import numpy as np
import matplotlib.pyplot as plt

def gen_shepp_logan(num_rows,num_cols):
    """
    Generate a Shepp Logan phantom
    
    Args: 
        num_rows: int, number of rows.
        num_cols: int, number of cols.

    Return:
        out_image: 2D array, num_rows*num_cols
    """

    # The function describing the phantom is defined as the sum of 10 ellipses inside a 2×2 square:
    sl_paras = [
        {'x0': 0.0, 'y0': 0.0, 'a': 0.69, 'b': 0.92, 'theta': 0, 'gray_level': 2.0},
        {'x0': 0.0, 'y0': -0.0184, 'a': 0.6624, 'b': 0.874, 'theta': 0, 'gray_level': -0.98},
        {'x0': 0.22, 'y0': 0.0, 'a': 0.11, 'b': 0.31, 'theta': -18, 'gray_level': -0.02},
        {'x0': -0.22, 'y0': 0.0, 'a': 0.16, 'b': 0.41, 'theta': 18, 'gray_level': -0.02},
        {'x0': 0.0, 'y0': 0.35, 'a': 0.21, 'b': 0.25, 'theta': 0, 'gray_level': 0.01},
        {'x0': 0.0, 'y0': 0.1, 'a': 0.046, 'b': 0.046, 'theta': 0, 'gray_level': 0.01},
        {'x0': 0.0, 'y0': -0.1, 'a': 0.046, 'b': 0.046, 'theta': 0, 'gray_level': 0.01},
        {'x0': -0.08, 'y0': -0.605, 'a': 0.046, 'b': 0.023, 'theta': 0, 'gray_level': 0.01},
        {'x0': 0.0, 'y0': -0.605, 'a': 0.023, 'b': 0.023, 'theta': 0, 'gray_level': 0.01},
        {'x0': 0.06, 'y0': -0.605, 'a': 0.023, 'b': 0.046, 'theta': 0, 'gray_level': 0.01}
    ]

    axis_x = np.linspace(-1.0, 1.0, num_cols)
    axis_y = np.linspace(1.0, -1.0, num_rows)

    x_grid, y_grid = np.meshgrid(axis_x, axis_y)
    image = x_grid * 0.0

    for el_paras in sl_paras:
        image += _gen_ellipse(x_grid=x_grid, y_grid=y_grid, x0=el_paras['x0'], y0=el_paras['y0'],
                             a=el_paras['a'], b=el_paras['b'], theta=el_paras['theta'] / 180.0 * np.pi,
                             gray_level=el_paras['gray_level'])

    return image


def gen_microscopy_sample(num_rows, num_cols):
    """
    Generate a microscopy sample phantom.

    Args:
        num_rows: int, number of rows.
        num_cols: int, number of cols.

    Return:
        out_image: 2D array, num_rows*num_cols
    """

    # The function describing the phantom is defined as the sum of 8 ellipses inside a 2×4 rectangle:
    ms_paras = [
        {'x0': 0.0, 'y0': -0.0184, 'a': 0.6624, 'b': 1.748, 'theta': 0, 'gray_level': 0.2},
        {'x0': -0.1, 'y0': 1.343, 'a': 0.11, 'b': 0.10, 'theta': 0, 'gray_level': 0.8},
        {'x0': 0.0, 'y0': 0.9, 'a': 0.33, 'b': 0.15, 'theta': 0, 'gray_level': 0.4},
        {'x0': 0.25, 'y0': 0.4, 'a': 0.1, 'b': 0.2, 'theta': 0, 'gray_level': 0.8},
        {'x0': -0.2, 'y0': 0.0, 'a': 0.2, 'b': 0.08, 'theta': 0, 'gray_level': 0.4},
        {'x0': 0.2, 'y0': -0.35, 'a': 0.1, 'b': 0.1, 'theta': 0, 'gray_level': 0.8},
        {'x0': 0.25, 'y0': -0.8, 'a': 0.2, 'b': 0.08, 'theta': 0, 'gray_level': 0.8},
        {'x0': -0.04, 'y0': -1.3, 'a': 0.33, 'b': 0.15, 'theta': 0, 'gray_level': 0.8}
    ]
    axis_x = np.linspace(-1, 1, num_cols)
    axis_y = np.linspace(2, -2, num_rows)

    x_grid, y_grid = np.meshgrid(axis_x, axis_y )
    image = x_grid * 0.0

    for el_paras in ms_paras:
        image += _gen_ellipse(x_grid=x_grid, y_grid=y_grid, x0=el_paras['x0'], y0=el_paras['y0'],
                             a=el_paras['a'], b=el_paras['b'], theta=el_paras['theta'] / 180.0 * np.pi,
                             gray_level=el_paras['gray_level'])

    return image


def gen_shepp_logan_3d(num_rows, num_cols, num_slices):
    """
    Generate a 3D Shepp Logan phantom based on below reference.
    
    Kak AC, Slaney M. Principles of computerized tomographic imaging. Page.102. IEEE Press, New York, 1988. https://engineering.purdue.edu/~malcolm/pct/CTI_Ch03.pdf

    Args:
        num_rows: int, number of rows.
        num_cols: int, number of cols.
        num_slices: int, number of slices.

    Return:
        out_image: 3D array, num_slices*num_rows*num_cols
    """

    # The function describing the phantom is defined as the sum of 10 ellipsoids inside a 2×2×2 cube:
    sl3d_paras = [
        {'x0': 0.0, 'y0': 0.0, 'z0': 0.0, 'a': 0.69, 'b': 0.92, 'c': 0.9, 'gamma': 0, 'gray_level': 2.0},
        {'x0': 0.0, 'y0': 0.0, 'z0': 0.0, 'a': 0.6624, 'b': 0.874, 'c': 0.88, 'gamma': 0, 'gray_level': -0.98},
        {'x0': -0.22, 'y0': 0.0, 'z0': -0.25, 'a': 0.41, 'b': 0.16, 'c': 0.21, 'gamma': 108, 'gray_level': -0.02},
        {'x0': 0.22, 'y0': 0.0, 'z0': -0.25, 'a': 0.31, 'b': 0.11, 'c': 0.22, 'gamma': 72, 'gray_level': -0.02},
        {'x0': 0.0, 'y0': 0.35, 'z0': -0.25, 'a': 0.21, 'b': 0.25, 'c': 0.5, 'gamma': 0, 'gray_level': 0.02},
        {'x0': 0.0, 'y0': 0.1, 'z0': -0.25, 'a': 0.046, 'b': 0.046, 'c': 0.046, 'gamma': 0, 'gray_level': 0.02},
        {'x0': -0.08, 'y0': -0.65, 'z0': -0.25, 'a': 0.046, 'b': 0.023, 'c': 0.02, 'gamma': 0, 'gray_level': 0.01},
        {'x0': 0.06, 'y0': -0.65, 'z0': -0.25, 'a': 0.046, 'b': 0.023, 'c': 0.02, 'gamma': 90, 'gray_level': 0.01},
        {'x0': 0.06, 'y0': -0.105, 'z0': 0.625, 'a': 0.056, 'b': 0.04, 'c': 0.1, 'gamma': 90, 'gray_level': 0.02},
        {'x0': 0.0, 'y0': 0.1, 'z0': 0.625, 'a': 0.056, 'b': 0.056, 'c': 0.1, 'gamma': 0, 'gray_level': -0.02}
    ]

    axis_x = np.linspace(-1.0, 1.0, num_cols)
    axis_y = np.linspace(1.0, -1.0, num_rows)
    axis_z = np.linspace(-1.0, 1.0, num_slices)

    x_grid, y_grid, z_grid = np.meshgrid(axis_x, axis_y, axis_z)
    image = x_grid * 0.0

    for el_paras in sl3d_paras:
        image += _gen_ellipsoid(x_grid=x_grid, y_grid=y_grid, z_grid=z_grid, x0=el_paras['x0'], y0=el_paras['y0'],
                               z0=el_paras['z0'],
                               a=el_paras['a'], b=el_paras['b'], c=el_paras['c'],
                               gamma=el_paras['gamma'] / 180.0 * np.pi,
                               gray_level=el_paras['gray_level'])

    return np.transpose(image, (2, 0, 1))


def gen_microscopy_sample_3d(num_rows, num_cols, num_slices):
    """
    Generate a 3D microscopy sample phantom.

    Args:
        num_rows: int, number of rows.
        num_cols: int, number of cols.
        num_slices: int, number of slices.

    Return:
        out_image: 3D array, num_slices*num_rows*num_cols
    """

    # The function describing the phantom is defined as the sum of 8 ellipsoids inside a 2×4×2 cuboid:
    ms3d_paras = [
        {'x0': 0.0, 'y0': -0.0184, 'z0':0.0, 'a': 0.6624, 'b': 1.748, 'c':0.8, 'gamma': 0, 'gray_level': 0.2},
        {'x0': -0.1, 'y0': 1.343, 'z0':0.0, 'a': 0.11, 'b': 0.10, 'c':0.20, 'gamma': 0, 'gray_level': 0.8},
        {'x0': 0.0, 'y0': 0.9, 'z0':0.0, 'a': 0.33, 'b': 0.15, 'c':0.66, 'gamma': 0, 'gray_level': 0.4},
        {'x0': 0.25, 'y0': 0.4, 'z0':0.0, 'a': 0.1, 'b': 0.2, 'c':0.40, 'gamma': 0, 'gray_level': 0.8},
        {'x0': -0.2, 'y0': 0.0, 'z0':0.0, 'a': 0.2, 'b': 0.08, 'c':0.40, 'gamma': 0, 'gray_level': 0.4},
        {'x0': 0.2, 'y0': -0.35, 'z0':0.0, 'a': 0.1, 'b': 0.1, 'c':0.2, 'gamma': 0, 'gray_level': 0.8},
        {'x0': 0.25, 'y0': -0.8, 'z0':0.0, 'a': 0.2, 'b': 0.08, 'c':0.4, 'gamma': 0, 'gray_level': 0.8},
        {'x0': -0.04, 'y0': -1.3, 'z0':0.0, 'a': 0.33, 'b': 0.15, 'c':0.30, 'gamma': 0, 'gray_level': 0.8}
    ]

    axis_x = np.linspace(-1.0, 1.0, num_cols)
    axis_y = np.linspace(2.0, -2.0, num_rows)
    axis_z = np.linspace(-1.0, 1.0, num_slices)

    x_grid, y_grid, z_grid = np.meshgrid(axis_x, axis_y, axis_z)
    image = x_grid * 0.0

    for el_paras in ms3d_paras:
        image += _gen_ellipsoid(x_grid=x_grid, y_grid=y_grid, z_grid=z_grid, x0=el_paras['x0'], y0=el_paras['y0'],
                               z0=el_paras['z0'],
                               a=el_paras['a'], b=el_paras['b'], c=el_paras['c'],
                               gamma=el_paras['gamma'] / 180.0 * np.pi,
                               gray_level=el_paras['gray_level'])

    return np.transpose(image, (2, 0, 1))

def nrmse(image, reference_image):
    """
    Compute the normalized root mean square error between image and reference_image.

    :param image: Calculated image
    :param reference_image: Ground truth image
    :return: Root mean square of (image - reference_image) divided by RMS of reference_image
    """

    rmse = np.sqrt(((image - reference_image) ** 2).mean())
    denominator = np.sqrt(((reference_image) ** 2).mean())

    return rmse/denominator

def plot_image(img, title=None, filename=None, vmin=None, vmax=None):
    """
    Function to display and save a 2D array as an image.
    :param img: 2D numpy array to display
    :param vmin: Value mapped to black
    :param vmax: Value mapped to white
    """

    plt.ion()
    fig = plt.figure()
    imgplot = plt.imshow(img, vmin=vmin, vmax=vmax)
    plt.title(label=title)
    imgplot.set_cmap('gray')
    plt.colorbar()
    plt.savefig(filename)


def _gen_ellipse(x_grid, y_grid, x0, y0, a, b, gray_level, theta=0):
    """
    Returns an image with a 2D ellipse in a 2D plane with a center of [x0,y0] and ...

    Args:
        x_grid(float): 2D grid of X coordinate values
        y_grid(float): 2D grid of Y coordinate values
        x0(float): horizontal center of ellipse.
        y0(float): vertical center of ellipse.
        a(float): X-axis radius.
        b(float): Y-axis radius.
        gray_level(float): Gray level for the ellipse.
        theta(float): [Default=0.0] counter-clockwise angle of rotation in radians

    Return:
        ndarray: 2D array with the same shape as x_grid and y_grid.

    """
    image = (((x_grid - x0) * np.cos(theta) + (y_grid - y0) * np.sin(theta)) ** 2 / a ** 2
             + ((x_grid - x0) * np.sin(theta) - (y_grid - y0) * np.cos(theta)) ** 2 / b ** 2 <= 1.0) * gray_level

    return image


def _gen_ellipsoid(x_grid, y_grid, z_grid, x0, y0, z0, a, b, c, gray_level, alpha=0, beta=0, gamma=0):
    """
    Returns an image with a 3D ellipsoid in a 3D plane with a center of [x0,y0,z0] and ...

    Args:
        x_grid(float): 3D grid of X coordinate values.
        y_grid(float): 3D grid of Y coordinate values.
        z_grid(float): 3D grid of Z coordinate values.
        x0(float): horizontal center of ellipsoid.
        y0(float): vertical center of ellipsoid.
        z0(float): normal center of ellipsoid.
        a(float): X-axis radius.
        b(float): Y-axis radius.
        c(float): Z-axis radius.
        gray_level(float): Gray level for the ellipse.
        alpha(float): [Default=0.0] counter-clockwise angle of rotation by X-axis in radians.
        beta(float): [Default=0.0] counter-clockwise angle of rotation by Y-axis in radians.
        gamma(float): [Default=0.0] counter-clockwise angle of rotation by Z-axis in radians.

    Return:
        ndarray: 3D array with the same shape as x_grid, y_grid, and z_grid

    """
    # Generate Rotation Matrix.
    rx = np.array([[1, 0, 0], [0, np.cos(-alpha), -np.sin(-alpha)], [0, np.sin(-alpha), np.cos(-alpha)]])
    ry = np.array([[np.cos(-beta), 0, np.sin(-beta)], [0, 1, 0], [-np.sin(-beta), 0, np.cos(-beta)]])
    rz = np.array([[np.cos(-gamma), -np.sin(-gamma), 0], [np.sin(-gamma), np.cos(-gamma), 0], [0, 0, 1]])
    r = np.dot(rx, np.dot(ry, rz))

    cor = np.array([x_grid.flatten() - x0, y_grid.flatten() - y0, z_grid.flatten() - z0])

    image = ((np.dot(r[0], cor)) ** 2 / a ** 2 + (np.dot(r[1], cor)) ** 2 / b ** 2 + (
        np.dot(r[2], cor)) ** 2 / c ** 2 <= 1.0) * gray_level

    return image.reshape(x_grid.shape)


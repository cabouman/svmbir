import numpy as np

def gen_shepp_logan(num_rows):
    """
    Generate a Shepp Logan phantom
    
    Args: 
        num_rows: int, number of rows.

    Return:
        out_image: 2D array, num_rows*num_cols
    """
    axis_rows=np.linspace(-1,1,num_rows)

    x_grid,y_grid = np.meshgrid(axis_rows,axis_rows)
    image = x_grid*0.0;

    image = image + gen_ellipse(x_grid=x_grid, y_grid=y_grid, x0=0, y0=0, a=0.69, b=0.92, gray_level=2.0 )

    return image


def gen_ellipse(x_grid,y_grid,x0,y0,a,b,gray_level,theta=0):
    """
    Returns an image with a 2D elipse in a 2D plane with a center of [x0,y0] and ...

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
    image = (((x_grid - x0) * np.cos(theta) + (y_grid - y0) * np.sin(theta)) ** 2 / a ** 2  \
    + ((x_grid - x0) * np.sin(theta) - (y_grid - y0) * np.cos(theta)) ** 2 / b <= 1.0)*gray_level

    return image



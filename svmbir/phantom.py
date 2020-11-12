import numpy as np

def gen_ellipse(x0,y0,a,b,value,pre_img,x_min,x_max,y_min,y_max,theta=0,add_value=False):
    """
    Draw ellipse in a 2D plane with range [x_min,x_max,y_min,y_max]. 

    There are two drawing modes in this function. 
    When add_value = False, this function will replace the ellipse area with given value.
    When add_value = True, this function will add value to pre_img's pixels which are inside ellipse area.
    
    Args: 
        x0(float): X-axis coordinate of center.
        y0(float): Y-axis coordinate of center.
        a(float): X-axis radius.
        b(float): Y-axis radius.
        value(float): Value of the ellipse.
        pre_img(float): Plane that the ellipse added to. 
        x_min(float): Minimum coordinate of X-axis.
        x_max(float): Maximum coordinate of X-axis.
        y_min(float): Minimum coordinate of Y-axis.
        y_max(float): Maximum coordinate of Y-axis.
        theta(float): [Default=0.0] Angle of rotation, from -PI to PI.
        add_value(bool): [Default=False] If add_value is True, add value to pre_img's pixels which are inside ellipse area.

    Return:
        ndarray: 2D array with the same shape of pre_img.

    """
    num_rows,num_cols=pre_img.shape
    axis_rows=np.linspace(x_min,x_max,num_cols)
    axis_cols=np.linspace(y_min,y_max,num_rows)
    x,y = np.meshgrid(axis_rows,axis_cols)

    if not add_value:    
        pre_img[((x-x0)*np.cos(theta)+(y-y0)*np.sin(theta))**2/a**2 \
        +((x-x0)*np.sin(theta)-(y-y0)*np.cos(theta))**2/b**2<=1]=value
        out_img=pre_img
    else:
        temp_img=((x-x0)*np.cos(theta)+(y-y0)*np.sin(theta))**2/a**2 \
        +((x-x0)*np.sin(theta)-(y-y0)*np.cos(theta))**2/b**2<=1
        out_img=pre_img+temp_img*value

    return out_img




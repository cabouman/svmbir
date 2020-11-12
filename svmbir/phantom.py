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

def gen_3D_SL_phantom(num_rows,num_cols):
    """
    Generate 3D slice phantom when given image shape.
    
    Args: 
        num_rows: int, number of rows.
        num_cols: int, number of cols.

    Return:
        out_image: 2D array, num_rows*num_cols

    """
    axis_rows=np.linspace(-1,1,num_cols)
    axis_cols=np.linspace(-1,1,num_rows)

    x,y = np.meshgrid(axis_rows,axis_cols)
    out_img=np.zeros((num_rows,num_cols))

    # Generate "a" ellipse
    x0=0
    y0=0
    ax=0.69
    ay=0.92
    out_img[((x-x0)/ax)**2 + ((y-y0)/ay)**2 <= 1]=255

    x0=0
    y0=-0.0184
    ax=0.6642
    ay=0.8740
    out_img[((x-x0)/ax)**2 + ((y-y0)/ay)**2 <= 1]=137

    x0=0
    y0=0.3500
    ax=0.21
    ay=0.25
    value=180
    out_img[((x-x0)/ax)**2 + ((y-y0)/ay)**2 <= 1]=value

    x0=0
    y0=0.100
    ax=0.046
    ay=0.046
    relative_value=30
    temp_img=((x-x0)/ax)**2 + ((y-y0)/ay)**2 <= 1
    out_img=out_img + relative_value*temp_img

    x0=-0.08
    y0=-0.605
    ax=0.046
    ay=0.023
    out_img[((x-x0)/ax)**2 + ((y-y0)/ay)**2 <= 1]=value

    x0=0
    y0=-0.606
    ax=0.023
    ay=0.023
    out_img[((x-x0)/ax)**2 + ((y-y0)/ay)**2 <= 1]=value

    x0=0.06
    y0=-0.605
    ax=0.023
    ay=0.046
    out_img[((x-x0)/ax)**2 + ((y-y0)/ay)**2 <= 1]=value

    x0=0
    y0=0
    ax=0.16
    ay=0.41
    relative_value=90
    rot_ang=np.pi/10
    temp_img=((x-x0)*np.cos(rot_ang)+(y-y0)*np.sin(rot_ang))**2/ax**2 +((x-x0)*np.sin(rot_ang)-(y-y0)*np.cos(rot_ang))**2/ay**2<=1
    shift=np.int(np.round(0.22/2*min(num_rows,num_cols)))

    ts=temp_img[:,shift:num_cols]
    zs=np.zeros((num_rows,shift))
    temp_img=np.concatenate((ts,zs), axis=1) 
    out_img = out_img - relative_value*temp_img   
    return out_img/255.0

def gen_3D_SL_MS_phantom(num_rows,num_cols):
    """
    Generate 3D slice microscopy when given image shape.
    
    Args: 
        num_rows: int, number of rows.
        num_cols: int, number of cols.

    Return:
        out_image: 2D array, num_rows*num_cols

    """
    axis_rows=np.linspace(-1.2,1.2,num_cols)
    axis_cols=np.linspace(-2.4,2.4,num_rows)

    x,y = np.meshgrid(axis_rows,axis_cols)
    out_img=np.zeros((num_rows,num_cols))


    x0=0
    y0=-0.0184
    ax=0.8642
    ay=2.012
    out_img[((x-x0)/ax)**2 + ((y-y0)/ay)**2 <= 1]=55

    x0=-0.1
    y0=-1.343
    ax=0.11
    ay=0.10
    value=180
    out_img[((x-x0)/ax)**2 + ((y-y0)/ay)**2 <= 1]=value

    x0=0
    y0=-0.9
    ax=0.33
    ay=0.15
    value=100
    out_img[((x-x0)/ax)**2 + ((y-y0)/ay)**2 <= 1]=value

    x0=0.2500
    y0=-0.4
    ax=0.1
    ay=0.2
    value=180
    out_img[((x-x0)/ax)**2 + ((y-y0)/ay)**2 <= 1]=value


    x0=-0.2
    y0=0
    ax=0.2
    ay=0.08
    value=100
    out_img[((x-x0)/ax)**2 + ((y-y0)/ay)**2 <= 1]=value

    x0=0.2000
    y0=0.3500
    ax=0.1
    ay=0.1
    value=180
    out_img[((x-x0)/ax)**2 + ((y-y0)/ay)**2 <= 1]=value

    x0=0.3
    y0=0.900
    ax=0.2
    ay=0.08
    value=180
    out_img[((x-x0)/ax)**2 + ((y-y0)/ay)**2 <= 1]=value

    x0=-0.04
    y0=1.3
    ax=0.33
    ay=0.15
    value=180
    out_img[((x-x0)/ax)**2 + ((y-y0)/ay)**2 <= 1]=value
   
    return out_img/255.0
def generate_3D_phantom(num_rows,num_cols, num_slice):
    """
    Generate 3D sample square phantom when given image size and number of slice. Rotate a 2D phantom to get a 3D sample phantom.
    
    Args: 
        num_rows: int, number of rows.
        num_cols: int, number of cols.
        num_slice: int, number of slice.

    Return:
        out_image: 3D array, num_slice*num_rows*num_cols

    """
    out_img=gen_3D_SL_phantom(num_rows,num_cols)
    out_vol=np.zeros((num_slice,num_rows+num_slice-1,num_cols+num_slice-1))
    for i in range(num_slice):
        out_vol[i,i:i+num_rows,i:i+num_cols]=out_img
    return out_vol


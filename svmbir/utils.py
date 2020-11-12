import numpy as np
import matplotlib.pyplot as plt
def gen_ellipse(x0,y0,a,b,value,pre_img,theta=0):
    """
    Generate ellipse in 2D plane.
    
    Args: 
        x0(float): X-axis coordinate.
        y0(float): Y-axis coordinate.
        a(float): X-axis radius.
        b(float): Y-axis radius.
        value(float): Value of the ellipse.
        pre_img(float): Plane that the ellipse added to. 
        theta(float): Angle of rotation, from -PI to PI.


    Return:
        ndarray: 2D array with the same shape of pre_img.

    """    
    pre_img[((x-x0)*np.cos(theta)+(y-y0)*np.sin(theta))**2/a**2 \
    +((x-x0)*np.sin(theta)-(y-y0)*np.cos(theta))**2/b**2<=1]=value

    return pre_img


if __name__ == '__main__':
    num_cols=256
    num_rows=256
    axis_rows=np.linspace(-1.2,1.2,num_cols)
    axis_cols=np.linspace(-2.4,2.4,num_rows)

    x,y = np.meshgrid(axis_rows,axis_cols)
    out_img=np.zeros((num_rows,num_cols))
    out_img=gen_ellipse(0,-0.0184,0.8642,2.012,55,out_img)

    imgplot = plt.imshow(out_img)
    imgplot.set_cmap('gray')
    plt.colorbar()
    #plt.savefig('test_gen_ellipse.png')
    plt.close()


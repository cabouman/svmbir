# svmbir.gui

*Python/QT GUI for svmbir 

## Installing svmbir.gui from source

First install the conda environment and svmbir from dev_scripts using

`source clean_install_all.sh`

Then 

`source install_gui.sh`

## Running svmbir.gui on sample data

First change to the demo directory and invoke 

`python demo_3D_shepp_logan.py`  

This will save a sample sinogram and set of angles for use with the gui.  

Next, change to the demo/output directory and invoke

`python ../../gui/main_gui.py`

This will start the gui.  Then load the sino file `shepp_logan_3D_sino.npy` and 
the angles file `shepp_logan_3D_angles.npy` and choose `Perform recon`.   
After the recon, the displayed parameters will be updated as calculated in recon.  
 
Hover the mouse over gui elements for tooltips as you continue to explore the gui functionality.  

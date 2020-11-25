import numpy as np
import svmbir


class Test_recon():
    def setup_method(self, method):
        np.random.seed(12345)

    def test_3d_shepp_logan_recon(self):
        # Set threshold for test
        threshold=0.05

        # Set simulation and phantom parameters
        num_rows=256
        num_cols=num_rows-1 # Test for nasty case of columns = rows-1
        num_views=144
        num_slices = 8

        # Reconstruction parameters
        T = 0.1
        p = 1.1
        sharpness = 0.0
        snr_db = 40.0

        try:
            phantom = svmbir.phantom.gen_shepp_logan_3d(num_rows, num_cols, num_slices)
        except Exception as e:
            print(e)
            assert 0

        angles = np.linspace(-np.pi/2.0, np.pi/2.0, num_views, endpoint=False)

        try: 
            sino = svmbir.project(angles,phantom,max(num_rows,num_cols))
        except Exception as e:
            print(e)
            assert 0

        (num_views, num_slices, num_channels) = sino.shape

        try:
            recon = svmbir.recon(sino, angles, num_rows=num_rows, num_cols=num_cols, T=T, p=p, sharpness=sharpness, snr_db=snr_db )
        except Exception as e:
            print(e)
            assert 0

        # Compute normalized root mean squared error of reconstruction
        nrmse = svmbir.phantom.nrmse(recon, phantom)

        assert nrmse<=threshold


    def test_multires_microscopy(self):
        # Set threshold for test
        threshold=0.05

        # Set simulation and phantom parameters
        num_rows = 256
        num_cols = 64
        num_slices = 16

        # Simulated sinogram parameters
        num_views = 64
        tilt_angle = np.pi / 2.3  # Tilt range of +-60deg

        # Reconstruction parameters
        sharpness = 2.0
        T = 0.25
        snr_db = 30.0
        p = 1.2

        # Display parameters
        vmin = 0.0
        vmax = 1.1

        # Generate phantom
        phantom = svmbir.phantom.gen_microscopy_sample_3d(num_rows, num_cols, num_slices)

        # Generate array of view angles form -180 to 180 degs
        angles = np.linspace(-tilt_angle, tilt_angle, num_views)

        # Generate sinogram by projecting phantom
        sino = svmbir.project(angles, phantom, max(num_rows, num_cols))

        # Determine resulting number of views, slices, and channels
        (num_views, num_slices, num_channels) = sino.shape

        # Perform fixed resolution MBIR reconstruction
        recon = svmbir.recon(sino, angles, num_rows=num_rows, num_cols=num_cols, max_resolutions=0, T=T,
                             p=p, sharpness=sharpness, snr_db=snr_db, stop_threshold=0.05)

        # Perform default MBIR reconstruction
        mr_recon = svmbir.recon(sino, angles, num_rows=num_rows, num_cols=num_cols, max_resolutions=2, T=T,
                             p=p, sharpness=sharpness, snr_db=snr_db, stop_threshold=0.05)

        # Compute Normalized Root Mean Squared Error
        nrmse = svmbir.phantom.nrmse(mr_recon, recon)

        assert nrmse<=threshold

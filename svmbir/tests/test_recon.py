import numpy as np
import svmbir


class Test_recon():
    def setup_method(self, method):
        np.random.seed(12345)

    def test_3_d_shepp_logan_recon(self):
        num_rows=256
        num_cols=num_rows-1 # Test for nasty case of columns = rows-1
        num_views=144
        num_slices = 8

        # Reconstruction parameters
        T = 0.1
        p = 1.1
        sharpness = 4.0
        snr_db = 40.0

        # Set threshold for test
        threshold=0.05

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





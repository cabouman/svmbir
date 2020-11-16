import numpy as np
import svmbir


class Test_recon():
    def setup_method(self, method):
        np.random.seed(12345)

    def test_shepp_logan_recon(self):
        num_rows=256
        num_cols=num_rows
        num_views=144 
        threshold=0.05

        try:
            phantom = svmbir.phantom.gen_shepp_logan(num_rows)
        except Exception as e:
            print(e)
            assert 0

        # Add singleton dimension for slices
        phantom = np.expand_dims(phantom,axis=0)
        
        angles = np.linspace(-np.pi/2.0, np.pi/2.0, num_views, endpoint=False)

        try: 
            sino = svmbir.project(angles,phantom,max(num_rows,num_cols))
        except Exception as e:
            print(e)
            assert 0

        (num_views, num_slices, num_channels) = sino.shape

        try:
            recon = svmbir.recon(sino, angles, sharpness=1.0, snr_db=40.0)
        except Exception as e:
            print(e)
            assert 0

        # Compute normalized root mean squared error of reconstruction
        nrmse = svmbir.phantom.nrmse(recon[0], phantom[0])

        assert nrmse<=threshold





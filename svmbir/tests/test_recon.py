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
            out_img = svmbir.phantom.gen_shepp_logan(num_rows)
        except Exception as e:
            print(e)
            assert 0

        out_img = np.expand_dims(out_img,axis=0)
        
        angles = np.linspace(-np.pi/2.0, np.pi/2.0, num_views, endpoint=False)

        try: 
            sino = svmbir.project(angles,out_img,max(num_rows,num_cols))
        except Exception as e:
            print(e)
            assert 0

        (num_views, num_slices, num_channels) = sino.shape

        try:
            x = svmbir.recon(sino, angles, sharpness=1.0, snr_db=40.0)
        except Exception as e:
            print(e)
            assert 0

        rmse=np.sqrt(np.linalg.norm(x[0]-out_img[0])**2/(out_img.shape[1]*out_img.shape[2]))
        assert rmse<=threshold





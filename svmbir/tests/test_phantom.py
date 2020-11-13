import numpy as np
import matplotlib.pyplot as plt
import svmbir


class Test_SVMBIR():
    def setup_method(self, method):
        np.random.seed(12345)

    def test_2D_recon(self):
        num_rows,num_cols=256,256

        try:
            out_img = svmbir.phantom.gen_Shepp_Logan(num_rows)
        except Exception as e:
            print(e)
            assert 0



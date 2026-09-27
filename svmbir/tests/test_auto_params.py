import numpy as np
import pytest
import svmbir


def test_auto_sigma_on_empty_sinogram_raises():
    sino = np.zeros((16, 2, 32), dtype=np.float32)
    with pytest.raises(ValueError, match="sinogram"):
        svmbir.auto_sigma_x(sino, delta_channel=1.0)
    with pytest.raises(ValueError, match="sinogram"):
        svmbir.auto_sigma_y(sino, snr_db=30.0, weights=np.ones_like(sino), delta_pixel=1.0)

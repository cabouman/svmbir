import warnings
import numpy as np
import svmbir._utils as utils


def _no_warnings(func, *args):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        return func(*args)


def test_numpy_scalars_are_accepted():
    sharpness, positivity, relax_factor, max_resolutions, stop_threshold, max_iterations = _no_warnings(
        utils.test_args_recon, np.float32(1.5), np.False_, np.float64(0.9), np.int64(1), np.int32(0), np.int64(20))
    assert (sharpness, positivity, relax_factor) == (1.5, False, 0.9)
    assert (max_resolutions, stop_threshold, max_iterations) == (1, 0.0, 20)
    assert type(positivity) is bool and type(max_iterations) is int

    num_threads, delete_temps, verbose = _no_warnings(utils.test_args_sys, np.int64(2), np.True_, np.int64(0))
    assert (num_threads, delete_temps, verbose) == (2, True, 0)

    num_rows, num_cols, delta_pixel, roi_radius, delta_channel, center_offset = _no_warnings(
        utils.test_args_geom, np.int64(64), np.int64(32), np.float32(1.0), None, np.float64(1.0), np.int64(2))
    assert (num_rows, num_cols, delta_pixel, delta_channel, center_offset) == (64, 32, 1.0, 1.0, 2.0)

    sigma_y, snr_db, sigma_x, sigma_p = _no_warnings(utils.test_args_noise, np.float32(1.0), np.int64(30), None, None)
    assert (sigma_y, snr_db) == (1.0, 30.0)

    p, q, T, b_interslice = _no_warnings(utils.test_args_qggmrf, np.float32(1.2), np.float64(2.0), np.int64(1), np.float32(1.0))
    assert (p, q, T, b_interslice) == (np.float32(1.2), 2.0, 1.0, 1.0)


def test_wrong_types_still_warn():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        sharpness, positivity, *_ = utils.test_args_recon("high", "yes", 1.0, None, 0.0, 10)
    assert (sharpness, positivity) == (0.0, True)
    assert len(caught) == 2

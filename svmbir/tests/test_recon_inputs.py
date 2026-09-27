import numpy as np
import pytest
import svmbir


def _small_problem():
    num_rows, num_cols, num_slices, num_views = 32, 32, 8, 16
    angles = np.linspace(0, np.pi, num_views, endpoint=False)
    phantom = svmbir.phantom.gen_shepp_logan_3d(num_rows, num_cols, num_slices)
    sino = svmbir.project(phantom, angles, num_cols)
    return phantom, sino, angles


def test_init_proj_gives_same_result_as_projecting():
    # init_proj is the projection of init_image.  With one thread the
    # reconstruction is deterministic, so passing init_proj must give exactly
    # the result of letting recon project the image itself.
    phantom, sino, angles = _small_problem()
    init_image = 0.5 * phantom
    init_proj = svmbir.project(init_image, angles, sino.shape[2])
    init_proj_saved = init_proj.copy()
    kwargs = dict(max_iterations=3, num_threads=1, max_resolutions=0, verbose=0)
    recon_with = svmbir.recon(sino, angles, init_image=init_image, init_proj=init_proj, **kwargs)
    recon_without = svmbir.recon(sino, angles, init_image=init_image, **kwargs)
    assert np.array_equal(recon_with, recon_without)
    assert np.array_equal(init_proj, init_proj_saved)


def test_init_proj_ignored_with_multiresolution():
    phantom, sino, angles = _small_problem()
    init_image = 0.5 * phantom
    init_proj = svmbir.project(init_image, angles, sino.shape[2])
    kwargs = dict(max_iterations=3, num_threads=1, max_resolutions=1, verbose=0)
    with pytest.warns(UserWarning, match="init_proj is ignored"):
        recon_with = svmbir.recon(sino, angles, init_image=init_image, init_proj=init_proj, **kwargs)
    recon_without = svmbir.recon(sino, angles, init_image=init_image, **kwargs)
    assert np.array_equal(recon_with, recon_without)


def test_init_image_is_not_modified():
    phantom, sino, angles = _small_problem()
    init_image = np.ascontiguousarray(0.5 * phantom, dtype=np.float32)
    init_image_saved = init_image.copy()
    recon = svmbir.recon(sino, angles, init_image=init_image, max_iterations=3, num_threads=1, verbose=0)
    assert recon is not init_image
    assert np.array_equal(init_image, init_image_saved)


def test_wrong_shapes_raise():
    phantom, sino, angles = _small_problem()
    with pytest.raises(ValueError, match="init_image"):
        svmbir.recon(sino, angles, init_image=phantom[:, ::2, ::2].copy(), max_iterations=1, verbose=0)
    with pytest.raises(ValueError, match="init_proj"):
        svmbir.recon(sino, angles, init_image=phantom, init_proj=sino[::2].copy(), max_iterations=1, verbose=0)


def test_recon_leaves_environment_unchanged():
    import os
    phantom, sino, angles = _small_problem()
    env_before = dict(os.environ)
    svmbir.recon(sino, angles, max_iterations=1, num_threads=1, verbose=0)
    svmbir.project(phantom, angles, sino.shape[2], num_threads=1)
    assert dict(os.environ) == env_before


def test_default_num_threads_honors_environment(monkeypatch):
    from svmbir.svmbir import _default_num_threads
    monkeypatch.setenv("OMP_NUM_THREADS", "3")
    assert _default_num_threads() == 3
    monkeypatch.setenv("OMP_NUM_THREADS", "junk")
    assert _default_num_threads() >= 1
    monkeypatch.delenv("OMP_NUM_THREADS")
    assert _default_num_threads() >= 1

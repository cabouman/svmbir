import numpy as np
from svmbir._utils import hash_params


def _geometry():
    return dict(geometry='parallel', Nx=64, Ny=64, delta_xy=1.0, roi_radius=32.0,
                num_channels=64, num_views=1200, delta_channel=1.0, center_offset=0.0,
                dist_source_detector=1.0, magnification=1.0)


def test_cache_key_uses_every_angle():
    # Two angle arrays with the same endpoints and different interiors must
    # give different keys.  numpy prints only the ends of an array longer
    # than 1000, so a key built from the printed text would not tell them apart.
    angles_a = np.linspace(0, np.pi, 1200, endpoint=False, dtype=np.single)
    angles_b = angles_a.copy()
    angles_b[4:-4] = angles_b[4:-4][::-1]
    key_a, _ = hash_params(angles_a, **_geometry())
    key_b, _ = hash_params(angles_b, **_geometry())
    assert key_a != key_b


def test_cache_key_is_deterministic():
    angles = np.linspace(0, np.pi, 1200, endpoint=False, dtype=np.single)
    key_1, _ = hash_params(angles, **_geometry())
    key_2, _ = hash_params(angles.copy(), **_geometry())
    assert key_1 == key_2
    params = _geometry()
    params['center_offset'] = 0.5
    key_3, _ = hash_params(angles, **params)
    assert key_3 != key_1

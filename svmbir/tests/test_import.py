import svmbir


def test_all_names_exist():
    for name in svmbir.__all__:
        assert hasattr(svmbir, name), name


def test_star_import():
    namespace = {}
    exec("from svmbir import *", namespace)
    assert "recon" in namespace and "_clear_cache" in namespace

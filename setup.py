import os
import sys
import numpy as np
from setuptools import setup, Extension
from Cython.Distutils import build_ext

src_dir = "svmbir/sv-mbirct/src/"

# Set up install for Cython or Command line interface
if os.environ.get('CLIB') != 'CMD_LINE':

    # Fail fast: Xcode Command Line Tools provide clang, git, and SDK headers on macOS.
    if sys.platform == 'darwin':
        import subprocess as _sp
        _xcode = _sp.run(['xcode-select', '-p'], capture_output=True)
        if _xcode.returncode != 0:
            sys.exit(
                "\nERROR: Xcode Command Line Tools are not installed.\n"
                "Run the following command and follow the prompts, then retry:\n\n"
                "    xcode-select --install\n"
            )

    # Fail fast: submodule must be initialized before compilation can proceed.
    import glob as _glob
    if not _glob.glob(src_dir + '*.c'):
        sys.exit(
            "\nERROR: C source files not found in " + src_dir + "\n"
            "The git submodule has not been initialized. Run:\n\n"
            "    git submodule update --init --recursive\n"
        )

    # On macOS, force clang unless the user explicitly chose something other than gcc.
    # Homebrew GCC at /usr/local is Intel-only and silently produces x86_64 binaries
    # on arm64 machines. We override both the unset case and the generic 'gcc' default
    # (which conda activation sometimes injects into the environment).
    if sys.platform == 'darwin':
        if os.environ.get('CC') in (None, 'gcc'):
            os.environ['CC'] = 'clang'
    elif os.environ.get('CC') is None:
        os.environ['CC'] = 'gcc'

    # Fail fast: verify the selected compiler is actually on PATH.
    import shutil as _shutil
    _cc = os.environ['CC']
    if _cc != 'msvc' and _shutil.which(_cc) is None:
        sys.exit(
            f"\nERROR: Compiler '{_cc}' not found in PATH.\n"
            "Set the CC environment variable to a compiler that is installed,\n"
            "e.g.:  CC=gcc pip install .   or   CC=clang pip install .\n"
        )

    if os.environ.get('CC') not in ['icc', 'clang', 'msvc']:
        extra_compile_args = ["-std=c11", "-O3", "-fopenmp", "-Wno-unknown-pragmas"]
        extra_link_args = ["-lm", "-fopenmp"]

    if os.environ.get('CC') == 'icc':
        if sys.platform == 'linux':
            os.environ['LDSHARED'] = 'icc -shared'
        extra_compile_args = ["-O3", "-DICC", "-qopenmp", "-no-prec-div", "-restrict",
                              "-inline-calloc", "-qopt-calloc", "-no-ansi-alias", "-xCORE-AVX2"]
        extra_link_args = ["-lm", "-qopenmp"]

    if os.environ.get('CC') == 'clang':
        import subprocess
        # Search for arm64 libomp in order of preference:
        #   1. CONDA_PREFIX — the active conda env, inherited even inside pip's
        #      build-isolation subprocess, so this works for both direct builds
        #      and `pip install`.
        #   2. sys.prefix — the Python env running this script (same as CONDA_PREFIX
        #      for direct invocations, different for pip build isolation).
        #   3. brew --prefix libomp — last resort; only reliable on native arm64
        #      Homebrew (/opt/homebrew). The Intel Homebrew at /usr/local ships an
        #      x86_64-only libomp that silently disables OpenMP at runtime on arm64.
        libomp_prefix = None
        for _candidate in filter(None, [
            os.environ.get('CONDA_PREFIX'),
            sys.prefix,
        ]):
            if os.path.exists(os.path.join(_candidate, 'lib', 'libomp.dylib')):
                libomp_prefix = _candidate
                break
        if libomp_prefix is None:
            try:
                _brew = subprocess.check_output(['brew', '--prefix', 'libomp'],
                                                text=True).strip()
                _dylib = os.path.join(_brew, 'lib', 'libomp.dylib')
                if os.path.exists(_dylib):
                    # Verify the library matches this machine's architecture.
                    # Intel Homebrew at /usr/local ships x86_64-only libomp; linking
                    # it into an arm64 build silently disables OpenMP at runtime.
                    import platform as _platform
                    _machine = _platform.machine()  # 'arm64' or 'x86_64'
                    _file_out = subprocess.run(['file', _dylib],
                                               capture_output=True, text=True).stdout
                    if _machine in _file_out:
                        libomp_prefix = _brew
            except Exception:
                pass
        # Fail fast: libomp is required on macOS; silent absence causes a dlopen crash.
        if libomp_prefix is None:
            sys.exit(
                "\nERROR: libomp not found. OpenMP is required on macOS.\n"
                "Install it into your active conda environment (recommended):\n\n"
                "    conda install -c conda-forge llvm-openmp\n\n"
                "Or, if using native arm64 Homebrew (/opt/homebrew):\n\n"
                "    brew install libomp\n"
            )
        extra_compile_args = ["-O3", "-Xclang", "-fopenmp", "-Wno-unknown-pragmas"]
        extra_link_args = ["-lm", "-lomp"]
        extra_compile_args += [f"-I{libomp_prefix}/include"]
        extra_link_args += [f"-L{libomp_prefix}/lib", f"-Wl,-rpath,{libomp_prefix}/lib"]

    if os.environ.get('CC') == 'msvc':
        extra_compile_args = ["/std:c11", "/O2", "/openmp", "/DMSVC"]
        extra_link_args = ["-lm"]

    c_extension = Extension("svmbir.interface_cy_c",
                            [src_dir + "A_comp.c", src_dir + "allocate.c", src_dir + "heap.c",
                             src_dir + "icd3d.c", src_dir + "initialize.c", src_dir + "MBIRModularUtils.c",
                             src_dir + "recon3d.c", "svmbir/interface_cy_c.pyx"],
                            libraries=[],
                            include_dirs=[np.get_include()],
                            define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')],
                            extra_compile_args=extra_compile_args,
                            extra_link_args=extra_link_args)

    package_data = {}
    cmdclass = {"build_ext": build_ext}
    ext_modules = [c_extension]

    # Set cython language level for all .pyx modules to Python 3.
    for e in ext_modules:
        e.cython_directives = {'language_level': "3"}

else:
    # Command-line interface install — requires a pre-compiled mbir_ct binary.
    if os.path.exists('svmbir/sv-mbirct/bin/mbir_ct'):
        exec_file = 'sv-mbirct/bin/mbir_ct'
    elif os.path.exists('svmbir/sv-mbirct/bin/mbir_ct.exe'):
        exec_file = 'sv-mbirct/bin/mbir_ct.exe'
    else:
        raise Exception(
            "Compiled executable not present in 'svmbir/sv-mbirct/bin/'. "
            "Compile the binary first."
        )
    package_data = {'svmbir': [exec_file]}
    cmdclass = {}
    ext_modules = None


setup(
    package_data=package_data,
    cmdclass=cmdclass,
    ext_modules=ext_modules,
)

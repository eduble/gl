try:
    import OpenGL
except:
    print('This module depends on PyOpenGL.')
    print('Please run "\033[1m!pip install -q pyopengl\033[0m" '
        'prior importing this module.')
    raise

import ctypes, sys, os

os.environ['PYOPENGL_PLATFORM'] = 'egl'

import OpenGL.GL as gl
import OpenGL.EGL as egl

gbm = ctypes.CDLL("libgbm.so.1") # On Ubuntu, package libgbm1

# computed from gbm.h
gbm.GBM_FORMAT_ARGB8888 = 875713089
gbm.GBM_BO_USE_RENDERING = 4

sys.modules['gbm'] = gbm

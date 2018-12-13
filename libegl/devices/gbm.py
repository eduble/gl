import os, glob, libgbm
import OpenGL.EGL as egl
from ctypes import pointer

class GBMSurface:
    def __init__(self, gbm_dev, egl_dpy, egl_config):
        self.gbm_dev, self.egl_dpy, self.egl_config = gbm_dev, egl_dpy, egl_config
        self.gbm_surf = None
        self.egl_surface = None
    def initialize(self, width, height):
        gbm_format = egl.EGLint()
        if not egl.eglGetConfigAttrib(self.egl_dpy, self.egl_config,
                            egl.EGL_NATIVE_VISUAL_ID, pointer(gbm_format)):
            return False
        self.gbm_surf = libgbm.gbm_surface_create(
                                        self.gbm_dev,
                                        width, height,
                                        gbm_format,
                                        libgbm.GBM_BO_USE_RENDERING)
        if not self.gbm_surf:
            self.gbm_surf = None
            return False
        self.egl_surface = egl.eglCreateWindowSurface(
                self.egl_dpy, self.egl_config, self.gbm_surf, None)
        if self.egl_surface == egl.EGL_NO_SURFACE:
            self.egl_surface = None
            self.release()
            return False
        return True
    def release(self):
        if self.gbm_surf is not None:
            libgbm.gbm_surface_destroy(self.gbm_surf)
        if self.egl_surface is not None:
            egl.eglDestroySurface(self.egl_dpy, self.egl_surface)
    def make_current(self, egl_context):
        return egl.eglMakeCurrent(self.egl_dpy, self.egl_surface, self.egl_surface, egl_context)

class GBMDevice:
    @staticmethod
    def probe():
        cards = sorted(glob.glob("/dev/dri/renderD*"))
        return [ GBMDevice(card) for card in cards ]
    def __init__(self, dev_path):
        self.dev_path = dev_path
        self.name = "GBM device " + dev_path
    def initialize(self):
        self.gbm_fd = os.open(self.dev_path, os.O_RDWR|os.O_CLOEXEC)
        if self.gbm_fd < 0:
            return False
        self.gbm_dev = libgbm.gbm_create_device(self.gbm_fd)
        if self.gbm_dev is None:
            os.close(self.gbm_fd)
            return False
        return True
    def release(self):
        libgbm.gbm_device_destroy(self.gbm_dev)
        os.close(self.gbm_fd)
    def compatible_surface_type(self):
        return egl.EGL_WINDOW_BIT
    def get_egl_display(self):
        return egl.eglGetDisplay(self.gbm_dev)
    def create_surface(self, egl_dpy, egl_config):
        return GBMSurface(self.gbm_dev, egl_dpy, egl_config)

#!/usr/bin/env python
import OpenGL.EGL as egl
from libegl import EGL_PLATFORM_DEVICE_EXT, EGL_DRM_DEVICE_FILE_EXT, egl_convert_to_int_array
from ctypes import pointer

class GenericEGLSurface:
    def __init__(self, egl_dpy, egl_config):
        self.egl_dpy, self.egl_config = egl_dpy, egl_config
    def initialize(self, width, height):
        pb_surf_attribs = egl_convert_to_int_array({
                egl.EGL_WIDTH: width,
                egl.EGL_HEIGHT: height,
        })
        self.egl_surface = egl.eglCreatePbufferSurface(
                self.egl_dpy, self.egl_config, pb_surf_attribs)
        if self.egl_surface == egl.EGL_NO_SURFACE:
            return False
        return True
    def release(self):
        egl.eglDestroySurface(self.egl_dpy, self.egl_surface)
    def make_current(self, egl_context):
        return egl.eglMakeCurrent(self.egl_dpy, self.egl_surface, self.egl_surface, egl_context)

class GenericEGLDevice:
    @staticmethod
    def probe():
        if not hasattr(egl, 'eglQueryDevicesEXT'):
            # if no enumeration support in EGL, return empty list
            return []
        num_devices = egl.EGLint()
        if not egl.eglQueryDevicesEXT(0, None, pointer(num_devices)) or num_devices.value < 1:
            return []
        devices = (egl.EGLDeviceEXT * num_devices.value)() # array of size num_devices
        if not egl.eglQueryDevicesEXT(num_devices.value, devices, pointer(num_devices)) or num_devices.value < 1:
            return []
        return [ GenericEGLDevice(devices[i]) for i in range(num_devices.value) ]
    def __init__(self, egl_dev):
        self.egl_dev = egl_dev
    def get_egl_display(self):
        return egl.eglGetPlatformDisplayEXT(EGL_PLATFORM_DEVICE_EXT, self.egl_dev, None)
    def initialize(self):
        return True
    def release(self):
        pass
    def compatible_surface_type(self):
        return egl.EGL_PBUFFER_BIT
    @property
    def name(self):
        if not hasattr(egl, 'eglQueryDeviceStringEXT'):
            return "EGL device unknown"
        devstr = egl.eglQueryDeviceStringEXT(self.egl_dev, EGL_DRM_DEVICE_FILE_EXT)
        return "EGL device " + devstr.decode('ASCII')
    def create_surface(self, egl_dpy, egl_config):
        return GenericEGLSurface(egl_dpy, egl_config)

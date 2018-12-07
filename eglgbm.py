#!/usr/bin/env python
import sys, os, glob, numpy as np
from ctypes import pointer
from collections import namedtuple
os.environ['PYOPENGL_PLATFORM'] = 'egl'
import OpenGL.GL as gl
import OpenGL.EGL as egl
import gbm

WIDTH = 32
HEIGHT = 32

Display = namedtuple('Display', ['gbm_fd', 'gbm', 'egl'])
Config = namedtuple('Config', ['dpy', 'egl'])
Window = namedtuple('Window', ['config', 'gbm', 'egl'])
Context = namedtuple('Context', ['window', 'egl'])

def abort():
    raise Exception('Aborted!')

def get_display():
    cards = sorted(glob.glob("/dev/dri/renderD*"))
    if not cards:
        raise RuntimeError("Need a /dev/dri/renderD* device to do rendering")
    if len(cards) > 1:
        print("Note, using first card: %s"%(cards[0]))
    gbm_fd = os.open(cards[0], os.O_RDWR|os.O_CLOEXEC)
    if gbm_fd < 0:
        abort()
    gbm_dev = gbm.gbm_create_device(gbm_fd)
    if gbm_dev is None:
        abort()
    egl_dpy = egl.eglGetDisplay(gbm_dev)
    if egl_dpy == egl.EGL_NO_DISPLAY:
        abort()
    major, minor = egl.EGLint(), egl.EGLint()
    if not egl.eglInitialize(egl_dpy, pointer(major), pointer(minor)):
        abort()
    return Display(gbm_fd, gbm_dev, egl_dpy)

def get_config(dpy):
    egl_config_attribs = [
        egl.EGL_BUFFER_SIZE,        32,           # 32-bits colors
        egl.EGL_DEPTH_SIZE,         egl.EGL_DONT_CARE,
        egl.EGL_STENCIL_SIZE,       egl.EGL_DONT_CARE,
        egl.EGL_RENDERABLE_TYPE,    egl.EGL_OPENGL_BIT,
        egl.EGL_SURFACE_TYPE,       egl.EGL_WINDOW_BIT,
        egl.EGL_NONE,
    ]
    egl_config_attribs = (egl.EGLint * len(egl_config_attribs))(*egl_config_attribs)
    num_configs = egl.EGLint()
    if not egl.eglGetConfigs(dpy.egl, None, 0, pointer(num_configs)):
        abort()
    print("found %d configs" % num_configs.value)
    if num_configs.value == 0:
        abort()
    configs = (egl.EGLConfig * num_configs.value)() # array of size num_configs
    if not egl.eglChooseConfig(dpy.egl, egl_config_attribs,
                        configs, num_configs, pointer(num_configs)):
        abort()
    # Find a config whose native visual ID is the desired GBM format.
    for i in range(num_configs.value):
        gbm_format = egl.EGLint()
        if not egl.eglGetConfigAttrib(dpy.egl, configs[i],
                                egl.EGL_NATIVE_VISUAL_ID, pointer(gbm_format)):
            abort()
        print("gbm_format %d" % gbm_format.value)
        if gbm_format.value == gbm.GBM_FORMAT_ARGB8888:
            return Config(dpy, configs[i])
    # Failed to find a config with matching GBM format.
    abort()

def get_window(config):
    gbm_surf = gbm.gbm_surface_create(config.dpy.gbm,
                                    WIDTH, HEIGHT,
                                    gbm.GBM_FORMAT_ARGB8888,
                                    gbm.GBM_BO_USE_RENDERING)
    if not gbm_surf:
        abort()
    egl_win = egl.eglCreateWindowSurface(config.dpy.egl,
                                        config.egl,
                                        gbm_surf,
                                        None)
    if egl_win == egl.EGL_NO_SURFACE:
        abort()
    return Window(config, gbm_surf, egl_win)

def get_context(window):
    if not egl.eglBindAPI(egl.EGL_OPENGL_API):
        abort()
    egl_context = egl.eglCreateContext(window.config.dpy.egl, window.config.egl, egl.EGL_NO_CONTEXT, None)
    if egl_context == egl.EGL_NO_CONTEXT:
        abort()
    if not egl.eglMakeCurrent(window.config.dpy.egl, window.egl, window.egl, egl_context):
        abort()
    return Context(window, egl_context)

def test():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glRecti(0, 0, 1, 1)
    img_buf = gl.glReadPixels(0, 0, WIDTH, HEIGHT, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
    # GL_RGB => 3 components per pixel
    img = np.frombuffer(img_buf, np.uint8).reshape(HEIGHT, WIDTH, 3)[::-1]
    print(img)
    return img

def main():
    dpy = get_display()
    config = get_config(dpy)
    window = get_window(config)
    context = get_context(window)
    return test()

if __name__ == '__main__':
    main()

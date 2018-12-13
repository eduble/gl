import ctypes
import numpy as np
import OpenGL.GL as gl

# only load libraries if they are needed
class LazyFuncCaller:
    libs = {}
    def __init__(self, lib_name, func_name):
        self.lib_name = lib_name
        self.func_name = func_name
    def __call__(self, *args, **kwargs):
        if self.lib_name not in LazyFuncCaller.libs:
            LazyFuncCaller.libs[self.lib_name] = ctypes.CDLL(self.lib_name)
        func = getattr(LazyFuncCaller.libs[self.lib_name], self.func_name)
        return func(*args, **kwargs)

# provide rollback capability to classes
class TransactionMixin:
    def __init__(self):
        self.rollback_cbs = []
    def rollback(self):
        for cb in reversed(self.rollback_cbs):
            cb()
        self.rollback_cbs = []
    def add_rollback_cb(self, cb):
        self.rollback_cbs += [ cb ]
    def __enter__(self):
        return self
    def __exit__(self, type, value, traceback):
        self.rollback()

PPM_HEADER = """\
P6
%(width)s %(height)s
255
"""

def write_ppm(filename, width, height):
    img_buf = gl.glReadPixels(0, 0, width, height, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
    # GL_RGB => 3 components per pixel
    img = np.frombuffer(img_buf, np.uint8).reshape(height, width, 3)[::-1]
    bin_data = img.tobytes('C')
    header = PPM_HEADER % dict(
        width = width,
        height = height
    )
    with open(filename, "wb") as f:
        f.write(header.encode('ASCII'))
        f.write(bin_data)
    print("image generated: " + filename)

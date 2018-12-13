#!/usr/bin/env python
import OpenGL.GL as gl
from libegl import EGLContext
from tools import write_ppm

WIDTH = 640
HEIGHT = 480

def draw():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    gl.glColor3f(0, 0, 1.0)
    x1, x2 = -0.9, 0.3
    y1, y2 = -0.5, 0.7
    gl.glRectf(x1, y1, x2, y2)

def main():
    with EGLContext() as ctx:
        if not ctx.initialize(WIDTH, HEIGHT):
            print('Sorry, could not initialize OpenGL context.')
            return
        draw()
        write_ppm("test.ppm", WIDTH, HEIGHT)

if __name__ == '__main__':
    main()

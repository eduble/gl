# OpenGL headless on linux (EGL+GBM): sample programs

This repository contains a sample program which runs **GPU computations (OpenGL) in headless mode (no display)**.
It is written in two versions:
* C language
* python

It is mostly based on the following sample codes and documentation:
* [khronos group doc about EGL+GBM](https://www.khronos.org/registry/EGL/extensions/MESA/EGL_MESA_platform_gbm.txt)
* [tensorflow/lucid sample python code](https://github.com/tensorflow/lucid/blob/master/lucid/misc/gl/glcontext.py)
* stackoverflow answers such as [this one](https://stackoverflow.com/questions/20816844/egldisplay-on-gbm)

# General notes

In any case, you need libGL, libEGL, libgbm.
For the C version, you also need development headers of these libraries.
On ubuntu, do:
```
$ apt install libgl1-mesa-dev libegl1-mesa-dev libgbm-dev
```

The program initializes an OpenGL context using GBM and EGL.
It will connect to kernel DRM interface file at `/dev/dri/renderD<something>`.

Then, to test if it works, it calls very basic OpenGL drawing functions (`glClear` and `glRecti`), and reads the image generated.

# C program notes

Run:
```
$ make
$ ./eglgbm
```

# Python program notes

You need PyOpenGL and numpy:
```
$ pip install wheel
$ pip install pyopengl numpy
```

On my machine, I also had to fix file `[python_dir]/site-packages/OpenGL/raw/EGL/_types.py`,
by applying [this modification](https://github.com/mcfletch/pyopengl/commit/47493f26d4b26e3a66e4070651dbf60e1ccf37f1).
It may be already fixed in your pyopengl distribution when you read this.

For more optimized transfers between PyOpenGL and numpy, do:
```
$ pip install Cython
$ pip install PyOpenGL_accelerate
```

Then you can run the program:
```
./eglgbm.py
```

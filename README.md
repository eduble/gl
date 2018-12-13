# OpenGL headless on linux (EGL): sample program

This repository contains a sample **python** program which runs **GPU computations (OpenGL) in headless mode (no display)**.

The program initializes an OpenGL context using EGL (and, optionally, GBM).
It will connect to kernel DRM interface file at `/dev/dri/<something>`.

Then, to test if it works, it calls very basic OpenGL drawing functions to draw a blue rectangle, and writes a ppm image file.

# Requirements

## OS libs

In any case, you need appropriate GPU drivers, with **libGL** and **libEGL**.
If you use a recent Nvidia driver, this will probably be enough.
Otherwise (intel integrated GPU for example), the program will try load **libgbm**.

For example on an ubuntu OS with a mesa-compatible GPU, the following should work:
```
$ apt install libgl1-mesa-dri libegl1-mesa libgbm1
```

## python libs

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

# How to run

To run the program, just type
```
$ ./main.py
```

# Links

The code is mostly based on the following sample codes and documentation:
* [This gist](https://gist.github.com/dcommander/ee1247362201552b2532)
* [khronos group doc about EGL+GBM](https://www.khronos.org/registry/EGL/extensions/MESA/EGL_MESA_platform_gbm.txt)
* [tensorflow/lucid sample python code](https://github.com/tensorflow/lucid/blob/master/lucid/misc/gl/glcontext.py),
  very useful reference for a Python version
* stackoverflow answers such as [this one](https://stackoverflow.com/questions/20816844/egldisplay-on-gbm)

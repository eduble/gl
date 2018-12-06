// This example program creates an EGL surface from a GBM surface.
//
// If the macro EGL_MESA_platform_gbm is defined, then the program
// creates the surfaces using the methods defined in this specification.
// Otherwise, it uses the methods defined by the EGL 1.4 specification.
//
// Compile with `cc -std=c99 example.c -lgbm -lEGL`.

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <EGL/egl.h>
#include <gbm.h>
#include <GL/gl.h>
//#include <GL/glu.h>

int WIDTH = 32;
int HEIGHT = 32;

struct my_display {
    struct gbm_device *gbm;
    EGLDisplay egl;
};

struct my_config {
    struct my_display dpy;
    EGLConfig egl;
};

struct my_window {
    struct my_config config;
    struct gbm_surface *gbm;
    EGLSurface egl;
};

struct my_context {
    struct my_window window;
    EGLContext egl;
};

static struct my_display
get_display(void)
{
    struct my_display dpy;

    int fd = open("/dev/dri/renderD128", O_RDWR | FD_CLOEXEC);
    if (fd < 0) {
        abort();
    }

    dpy.gbm = gbm_create_device(fd);
    if (!dpy.gbm) {
        abort();
    }

    dpy.egl = eglGetDisplay((EGLNativeDisplayType)dpy.gbm);

    if (dpy.egl == EGL_NO_DISPLAY) {
        abort();
    }

    EGLint major, minor;
    if (!eglInitialize(dpy.egl, &major, &minor)) {
        abort();
    }

    return dpy;
}

static struct my_config
get_config(struct my_display dpy)
{
    struct my_config config = {
        .dpy = dpy,
    };

    EGLint egl_config_attribs[] = {
        EGL_BUFFER_SIZE,        32,
        EGL_DEPTH_SIZE,         EGL_DONT_CARE,
        EGL_STENCIL_SIZE,       EGL_DONT_CARE,
        EGL_RENDERABLE_TYPE,    EGL_OPENGL_BIT,
        EGL_SURFACE_TYPE,       EGL_WINDOW_BIT,
        EGL_NONE,
    };

    EGLint num_configs;
    if (!eglGetConfigs(dpy.egl, NULL, 0, &num_configs)) {
        abort();
    }

    printf("found %d configs\n", num_configs);
    EGLConfig *configs = malloc(num_configs * sizeof(EGLConfig));
    if (!eglChooseConfig(dpy.egl, egl_config_attribs,
                         configs, num_configs, &num_configs)) {
        abort();
    }
    if (num_configs == 0) {
        abort();
    }

    // Find a config whose native visual ID is the desired GBM format.
    for (int i = 0; i < num_configs; ++i) {
        EGLint gbm_format;

        if (!eglGetConfigAttrib(dpy.egl, configs[i],
                                EGL_NATIVE_VISUAL_ID, &gbm_format)) {
            abort();
        }

        printf("gbm_format %d\n", gbm_format);
        if (gbm_format == GBM_FORMAT_ARGB8888) {
            config.egl = configs[i];
            free(configs);
            return config;
        }
    }

    // Failed to find a config with matching GBM format.
    abort();
}

static struct my_window
get_window(struct my_config config)
{
    struct my_window window = {
        .config = config,
    };

    window.gbm = gbm_surface_create(config.dpy.gbm,
                                    WIDTH, HEIGHT,
                                    GBM_FORMAT_ARGB8888,
                                    GBM_BO_USE_RENDERING);
    if (!window.gbm) {
        abort();
    }

    window.egl = eglCreateWindowSurface(config.dpy.egl,
                                        config.egl,
                                        (EGLNativeWindowType)window.gbm,
                                        NULL);

    if (window.egl == EGL_NO_SURFACE) {
        abort();
    }

    return window;
}

static struct my_context
get_context(struct my_window window)
{
    struct my_context context = {
        .window = window,
    };

    if (!eglBindAPI(EGL_OPENGL_API)) {
        abort();
    }

    context.egl = eglCreateContext(window.config.dpy.egl, window.config.egl, EGL_NO_CONTEXT, NULL);
    if (context.egl == EGL_NO_CONTEXT) {
        abort();
    }

    if (!eglMakeCurrent(window.config.dpy.egl, window.egl, window.egl, context.egl)) {
        abort();
    }

    return context;
}

int test() {
    int row, col;
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glRecti(0, 0, 1, 1);

    GLubyte *pixel_data = malloc(3 * WIDTH * HEIGHT); // GL_RGB => 3 components per pixel
    glReadPixels(0, 0, WIDTH, HEIGHT, GL_RGB, GL_UNSIGNED_BYTE, pixel_data);

    GLubyte red, green, blue, *pcolor = pixel_data;
    for (row = 0; row < HEIGHT; ++row)
    {
        for (col = 0; col < WIDTH; ++col)
        {
            red = *pcolor; ++pcolor;
            green = *pcolor; ++pcolor;
            blue = *pcolor; ++pcolor;
            printf("%c", (red < 128)?'*':' ');
        }
        printf("\n");
    }
}

int
main(void)
{
    struct my_display dpy = get_display();
    struct my_config config = get_config(dpy);
    struct my_window window = get_window(config);
    struct my_context context = get_context(window);

    test();

    return 0;
}

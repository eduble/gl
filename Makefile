
eglgbm: egl-gbm.c
	gcc -g -Og -std=c99 -o eglgbm egl-gbm.c -lgbm -lEGL -lGL

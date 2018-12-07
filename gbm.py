import ctypes

# calls to compiled library
lib = ctypes.CDLL("libgbm.so.1") # On Ubuntu, package libgbm1
gbm_create_device = lib.gbm_create_device
gbm_surface_create = lib.gbm_surface_create

# computed from gbm.h
GBM_FORMAT_ARGB8888 = 875713089
GBM_BO_USE_RENDERING = 4



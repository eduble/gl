from tools import LazyFuncCaller

LIB_NAME = "libgbm.so.1"  # On Ubuntu, package libgbm1

# calls to compiled library
gbm_create_device = LazyFuncCaller(LIB_NAME, 'gbm_create_device')
gbm_device_destroy = LazyFuncCaller(LIB_NAME, 'gbm_device_destroy')
gbm_surface_create = LazyFuncCaller(LIB_NAME, 'gbm_surface_create')
gbm_surface_destroy = LazyFuncCaller(LIB_NAME, 'gbm_surface_destroy')

# found in gbm.h
GBM_BO_USE_RENDERING = 4



from libegl.devices.generic import GenericEGLDevice
from libegl.devices.gbm import GBMDevice

def probe():
    for cls in (GenericEGLDevice, GBMDevice):
        for device in cls.probe():
            yield device

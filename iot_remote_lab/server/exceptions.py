"""
Custom exceptions for IoT Remote Lab
"""


class IoTRemoteLabError(Exception):
    """Base exception for IoT Remote Lab"""
    pass


class DeviceError(IoTRemoteLabError):
    """Device-related errors"""
    pass


class PlatformIOError(DeviceError):
    """PlatformIO command errors"""
    pass


class DeviceNotFoundError(DeviceError):
    """Device not found error"""
    pass


class DeviceConnectionError(DeviceError):
    """Device connection error"""
    pass


class ConfigurationError(IoTRemoteLabError):
    """Configuration-related errors"""
    pass
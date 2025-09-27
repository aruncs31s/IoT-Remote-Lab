import logging

from iot_remote_lab.core.device_manager.platformio.commands import \
    DeviceManager
from iot_remote_lab.core.device_manager.platformio.model import Device

from ..exceptions import DeviceError, PlatformIOError

# from ..utils.logging_config import get_logger


def device_list(logger: logging.Logger, dmg: DeviceManager) -> tuple[list[Device], str]:
    """Device list page"""
    try:
        logger.info("Loading device list page")
        # devices: list[Device] = device_list()
        """For Now using mock data"""
        devices: list[Device] = dmg.get_mock_data()
        return (devices, "")

    except (DeviceError, PlatformIOError) as e:
        logger.error(f"Device error on device list page: {str(e)}")
        return ([], str(e))

    except Exception as e:
        logger.error(f"Unexpected error on device list page: {str(e)}")
        return ([], "Failed to load devices")

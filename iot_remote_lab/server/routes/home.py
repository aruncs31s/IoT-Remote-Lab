import logging

from iot_remote_lab.core.device_manager.platformio.commands import \
    DeviceManager
from iot_remote_lab.core.device_manager.platformio.model import Device

from ..exceptions import DeviceError, PlatformIOError

# from ..utils.logging_config import get_logger


def home_page(logger: logging.Logger, dmg: DeviceManager) -> tuple[list[Device], str]:
    """Home page displaying ESP devices"""
    try:
        logger.info("Loading home page with device list")
        # devices: list[Device] = device_list()
        """For Now using mock data"""
        devices: list[Device] = dmg.get_mock_data()
        print("devices ", devices)
        return (devices, "")

    except (DeviceError, PlatformIOError) as e:
        logger.error(f"Device error on home page: {str(e)}")
        return ([], str(e))

    except Exception as e:
        logger.error(f"Unexpected error on home page: {str(e)}")
        # Fall back to the main home template to avoid TemplateNotFound
        return ([], "Failed to load devices")

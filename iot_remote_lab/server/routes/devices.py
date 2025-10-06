import logging

from flask import render_template

from iot_remote_lab.core.device_manager.platformio.commands import \
    DeviceManager
from iot_remote_lab.core.device_manager.platformio.model import Device

from ..exceptions import DeviceError, PlatformIOError


def device_list_view(logger: logging.Logger, dmg: DeviceManager):
    """Device list page"""
    try:
        logger.info("Loading device list page")
        # devices: list[Device] = device_list()
        """For Now using mock data"""
        devices: list[Device] = dmg.get_mock_data()
        return render_template("device_list.html", devices=devices)

    except (DeviceError, PlatformIOError) as e:
        logger.error(f"Device error on device list page: {str(e)}")
        return render_template("device_list.html", devices=[], error=str(e))

    except Exception as e:
        logger.error(f"Unexpected error on device list page: {str(e)}")
        return render_template("device_list.html", devices=[], error=str(e))

import logging

from flask import render_template

from iot_remote_lab.core.device_manager.platformio.commands import \
    DeviceManager
from iot_remote_lab.core.device_manager.platformio.model import Device

from ..exceptions import DeviceError, PlatformIOError


def home_page_view(logger: logging.Logger, dmg: DeviceManager):
    """Home page displaying ESP devices"""
    try:
        logger.info("Loading home page with device list")
        # devices: list[Device] = device_list()
        """For Now using mock data"""
        devices: list[Device] = dmg.get_mock_data()
        return render_template("home.html", devices=devices)

    except (DeviceError, PlatformIOError) as e:
        logger.error(f"Device error on home page: {str(e)}")
        return render_template("home.html", devices=[], error=str(e))

    except Exception as e:
        logger.error(f"Unexpected error on home page: {str(e)}")
        # Fall back to the main home template to avoid TemplateNotFound
        return render_template("home.html", devices=[], error=str(e))

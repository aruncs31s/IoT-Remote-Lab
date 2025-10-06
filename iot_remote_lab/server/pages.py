from flask import Blueprint, render_template

try:
    from utils.logging_config import get_logger

    from iot_remote_lab.core.device_manager.platformio.commands import \
        DeviceManager
except ImportError:
    from .utils.logging_config import get_logger
    from ..core.device_manager.platformio.commands import DeviceManager

from .routes import device_list_view, home_page_view

# Initialize logger
logger = get_logger("pages")

# Create pages blueprint
pages_bp = Blueprint("pages", __name__)

# Singleton DeviceManager instance
dmg = DeviceManager()


@pages_bp.route("/")
def home():
    return home_page_view(logger=logger, dmg=dmg)


@pages_bp.route("/devices")
def device_list_page():
    return device_list_view(logger=logger, dmg=dmg)


@pages_bp.route("/simulator")
def simulator():
    """ESP device simulator page"""
    try:
        logger.info("Loading simulator page")
        return render_template("simulator.html")

    except Exception as e:
        logger.error(f"Unexpected error on simulator page: {str(e)}")
        return render_template("simulator.html", error="Failed to load simulator")


@pages_bp.route("/programmer")
def programmer():
    """C++ code programmer page"""
    try:
        logger.info("Loading programmer page")
        return render_template("programmer.html")

    except Exception as e:
        logger.error(f"Unexpected error on programmer page: {str(e)}")
        return render_template("programmer.html", error="Failed to load programmer")


@pages_bp.route("/serial-monitor")
def serial_monitor():
    """Serial Monitor page"""
    try:
        logger.info("Loading serial monitor page")
        return render_template("serial_monitor.html")

    except Exception as e:
        logger.error(f"Unexpected error on serial monitor page: {str(e)}")
        return render_template(
            "serial_monitor.html", error="Failed to load serial monitor"
        )

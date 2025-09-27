import logging

from flask import Flask, jsonify, render_template, request

# from controllers.platformio_helper import device_list
# from controllers.platformio_helper.devices import Device
try:
    from config import get_config
    from exceptions import DeviceError, PlatformIOError
    from utils.logging_config import get_logger, setup_logging

    from iot_remote_lab.core.device_manager.platformio.commands import \
        DeviceManager
    from iot_remote_lab.core.device_manager.platformio.model import (
        Device, DeviceState)
except ImportError:
    from ..core.device_manager.platformio.commands import DeviceManager
    from ..core.device_manager.platformio.model import Device
    from .config import get_config
    from .exceptions import DeviceError, PlatformIOError
    from .utils.logging_config import get_logger, setup_logging

# Custom Imports
try:
    from utils.programms import (list_all_programs, load_program_from_file,
                                 save_program_to_file)
except ImportError:
    from .utils.programms import (list_all_programs, load_program_from_file,
                                  save_program_to_file)

# Initialize configuration and logging
config = get_config()
setup_logging(config.LOG_LEVEL)
logger = get_logger("app")

app = Flask(__name__)
app.config.from_object(config)

# Singleton DeviceManager instance
dmg = DeviceManager()

# Serve static files in development
# if app.config.get("ENV") != "production":
#     import os
#
#     from werkzeug.middleware.shared_data import SharedDataMiddleware
#
#     app.wsgi_app = SharedDataMiddleware(
#         app.wsgi_app, {"/static": os.path.join(os.path.dirname(__file__), "static")}
#     )
#
""" Pages """
from .routes import device_list, home_page


@app.route("/healthz")
def healthz():
    return jsonify({"ok": True}), 200


@app.route("/")
def home():
    """Home page displaying ESP devices"""
    devices, err = home_page(logger, dmg)
    if err != "":
        return render_template("home.html", devices=[], error=err)
    return render_template("home.html", devices=devices)


@app.route("/api/devices", methods=["GET"])
def get_devices():
    """Get list of connected devices"""
    try:
        logger.info("Requesting device list")
        # Use real device list if available; otherwise fall back to mock
        try:
            devices: list[Device] = dmg.get_devices()
        except Exception:
            logger.warning("Falling back to mock device data for /api/devices")
            devices = dmg.get_mock_data()
        json_devices = [device.to_dict() for device in devices]

        logger.info(f"Returning {len(json_devices)} devices")
        return jsonify(
            {
                "success": True,
                "data": json_devices,
                "devices": json_devices,
                "count": len(json_devices),
            }
        )

    except (DeviceError, PlatformIOError) as e:
        logger.error(f"Device error: {str(e)}")
        return jsonify({"success": False, "error": str(e), "type": "device_error"}), 500

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Internal server error",
                    "type": "server_error",
                }
            ),
            500,
        )


@app.route("/devices")
def device_list_page():
    """Device list page"""
    devices, err = device_list(logger, dmg)
    if err != "":
        return render_template("device_list.html", devices=[], error=err)
    return render_template("device_list.html", devices=devices)


@app.route("/simulator")
def simulator():
    """ESP device simulator page"""
    try:
        logger.info("Loading simulator page")
        return render_template("simulator.html")

    except Exception as e:
        logger.error(f"Unexpected error on simulator page: {str(e)}")
        return render_template("simulator.html", error="Failed to load simulator")


@app.route("/programmer")
def programmer():
    """C++ code programmer page"""
    try:
        logger.info("Loading programmer page")
        return render_template("programmer.html")

    except Exception as e:
        logger.error(f"Unexpected error on programmer page: {str(e)}")
        return render_template("programmer.html", error="Failed to load programmer")


@app.route("/serial-monitor")
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


@app.route("/api/save_program", methods=["POST"])
def save_program():
    return save_program_to_file(logger)


@app.route("/api/load_program/<program_name>")
def load_program(program_name):
    return load_program_from_file(logger, program_name)


@app.route("/api/list_programs")
def list_programs():
    return list_all_programs(logger)


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "success": True,
            "status": "healthy",
            "message": "IoT Remote Lab server is running",
        }
    )


@app.route("/api/upload_firmware", methods=["POST"])
def upload_firmware():
    """Upload firmware to a device"""
    # try:
    data = request.get_json()
    device: dict[str, str] = data.get("device", {})
    if not device or "port" not in device:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Device information with valid port is required",
                    "type": "invalid_device",
                }
            ),
            400,
        )

    program_name: str = data.get("program_name")
    port: str = device.get("port").strip()
    print("device is", port)
    device_obj = dmg.get_device_by_port(port.strip())
    print("device obj is", device_obj, " ids", id(device_obj))

    path = os.path.join(os.getcwd(), "programs", program_name)
    if not os.path.exists(path):
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Program {program_name} does not exist",
                    "type": "program_not_found",
                }
            ),
            404,
        )
    status, err = dmg.upload_firmware(device=device_obj, build_path=path, env="")
    if err != "" or not status:
        return (
            jsonify(
                {
                    "success": False,
                    "error": err,
                    "type": "upload_error",
                }
            ),
            500,
        )
    print(status, err)
    print("path is", path)
    return jsonify(
        {
            "success": status,
            "message": f"Firmware upload {device} with program {program_name} initiated",
        }
    )


# Serial Monitor API endpoints
@app.route("/api/serial/connect", methods=["POST"])
def serial_connect():
    """Connect to a device for serial monitoring"""
    try:
        data = request.get_json()
        device_data = data.get("device")
        baud_rate = data.get("baud_rate", 115200)

        if not device_data:
            return (
                jsonify({"success": False, "error": "Device information is required"}),
                400,
            )

        # Here you would implement actual serial connection logic
        # For now, return a mock success response
        logger.info(
            f"Serial connect request for device: {device_data.get('name', 'Unknown')}"
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": f"Connected to {device_data.get('name', 'device')}",
                    "session_id": "mock_session_123",  # Generate actual session ID
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Serial connect error: {str(e)}")
        return jsonify({"success": False, "error": "Failed to connect to device"}), 500


@app.route("/api/serial/disconnect", methods=["POST"])
def serial_disconnect():
    """Disconnect from serial device"""
    try:
        data = request.get_json()
        device_data = data.get("device")

        logger.info(
            f"Serial disconnect request for device: {device_data.get('name', 'Unknown') if device_data else 'Unknown'}"
        )

        # Here you would implement actual disconnection logic

        return jsonify({"success": True, "message": "Disconnected from device"}), 200

    except Exception as e:
        logger.error(f"Serial disconnect error: {str(e)}")
        return (
            jsonify({"success": False, "error": "Failed to disconnect from device"}),
            500,
        )


@app.route("/api/serial/send", methods=["POST"])
def serial_send():
    """Send data to serial device"""
    try:
        data = request.get_json()
        device_data = data.get("device")
        serial_data = data.get("data")

        if not serial_data:
            return jsonify({"success": False, "error": "Data is required"}), 400

        logger.info(f"Serial send request: {len(serial_data)} bytes")

        # Here you would implement actual data sending logic

        return jsonify({"success": True, "message": "Data sent successfully"}), 200

    except Exception as e:
        logger.error(f"Serial send error: {str(e)}")
        return jsonify({"success": False, "error": "Failed to send data"}), 500


@app.route("/api/serial/baud_rate", methods=["POST"])
def serial_baud_rate():
    """Update baud rate for serial connection"""
    try:
        data = request.get_json()
        device_data = data.get("device")
        baud_rate = data.get("baud_rate")

        if not baud_rate:
            return jsonify({"success": False, "error": "Baud rate is required"}), 400

        logger.info(f"Serial baud rate update request: {baud_rate}")

        # Here you would implement actual baud rate update logic

        return (
            jsonify({"success": True, "message": f"Baud rate updated to {baud_rate}"}),
            200,
        )

    except Exception as e:
        logger.error(f"Serial baud rate error: {str(e)}")
        return jsonify({"success": False, "error": "Failed to update baud rate"}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return (
        jsonify({"success": False, "error": "Endpoint not found", "type": "not_found"}),
        404,
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return (
        jsonify(
            {"success": False, "error": "Internal server error", "type": "server_error"}
        ),
        500,
    )


def main():
    logger.info(f"Starting IoT Remote Lab server on {config.HOST}:{config.PORT}")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)

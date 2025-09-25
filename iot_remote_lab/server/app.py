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
if app.config.get("ENV") != "production":
    import os

    from werkzeug.middleware.shared_data import SharedDataMiddleware

    app.wsgi_app = SharedDataMiddleware(
        app.wsgi_app, {"/static": os.path.join(os.path.dirname(__file__), "static")}
    )


@app.route("/healthz")
def healthz():
    return jsonify({"ok": True}), 200


@app.route("/")
def home():
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
        return render_template("home.html", devices=[], error="Failed to load devices")


@app.route("/new")
def new_home():
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
        return render_template("home.html", devices=[], error="Failed to load devices")


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
            {"success": True, "data": json_devices, "count": len(json_devices)}
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
        return render_template(
            "device_list.html", devices=[], error="Failed to load devices"
        )


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


@app.route("/api/save_program", methods=["POST"])
def save_program():
    return save_program_to_file(logger)
    # """Save C++ program to file system"""
    # import json
    # import os
    # from datetime import datetime
    #
    # try:
    #     data = request.get_json()
    #     program_name = data.get("program_name", "").strip()
    #     code = data.get("code", "")
    #
    #     if not program_name:
    #         return jsonify({"success": False, "error": "Program name is required"}), 400
    #
    #     if not code.strip():
    #         return jsonify({"success": False, "error": "Code cannot be empty"}), 400
    #
    #     # Create programs directory if it doesn't exist
    #     programs_dir = os.path.join(os.getcwd(), "programs")
    #     if not os.path.exists(programs_dir):
    #         os.makedirs(programs_dir)
    #
    #     # Create program-specific folder
    #     program_folder = os.path.join(programs_dir, program_name)
    #     if not os.path.exists(program_folder):
    #         os.makedirs(program_folder)
    #
    #     # Save main.cpp file
    #     cpp_file_path = os.path.join(program_folder, "main.cpp")
    #     with open(cpp_file_path, "w", encoding="utf-8") as f:
    #         f.write(code)
    #
    #     # Create metadata file
    #     metadata = {
    #         "program_name": program_name,
    #         "created_at": datetime.now().isoformat(),
    #         "file_path": cpp_file_path,
    #         "description": data.get("description", ""),
    #     }
    #
    #     metadata_file_path = os.path.join(program_folder, "metadata.json")
    #     with open(metadata_file_path, "w", encoding="utf-8") as f:
    #         json.dump(metadata, f, indent=2)
    #
    #     logger.info(f"Program '{program_name}' saved successfully to {program_folder}")
    #
    #     return jsonify(
    #         {
    #             "success": True,
    #             "message": f'Program "{program_name}" saved successfully',
    #             "file_path": cpp_file_path,
    #             "folder_path": program_folder,
    #         }
    #     )
    #
    # except Exception as e:
    #     logger.error(f"Error saving program: {str(e)}")
    #     return (
    #         jsonify({"success": False, "error": f"Failed to save program: {str(e)}"}),
    #         500,
    #     )


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
    try:
        data = request.get_json()
        device_id = data.get("device_id")
        firmware_data = data.get("firmware_data")

        if not device_id or not firmware_data:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "device_id and firmware_data are required",
                    }
                ),
                400,
            )

        logger.info(f"Uploading firmware to device {device_id}")
        # Simulate firmware upload
        # In real implementation, interact with DeviceManager or similar
        # For now, just log and return success
        logger.info(f"Firmware uploaded to device {device_id} successfully")

        return jsonify(
            {"success": True, "message": f"Firmware uploaded to device {device_id}"}
        )

    except Exception as e:
        logger.error(f"Error uploading firmware: {str(e)}")
        return (
            jsonify(
                {"success": False, "error": f"Failed to upload firmware: {str(e)}"}
            ),
            500,
        )


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

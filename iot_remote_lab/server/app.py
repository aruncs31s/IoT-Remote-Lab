from flask import Flask, jsonify, request, render_template
# from controllers.platformio_helper import device_list
# from controllers.platformio_helper.devices import Device
try:
    from iot_remote_lab.core.device_manager.platformio.model import Device
    from iot_remote_lab.core.device_manager.platformio.commands import get_devices as device_list 
    from iot_remote_lab.core.device_manager.platformio.commands import get_mock_data
    from exceptions import DeviceError, PlatformIOError
    from config import get_config
    from utils.logging_config import setup_logging, get_logger
except ImportError:
    from ..core.device_manager.platformio.model import Device
    from ..core.device_manager.platformio.commands import get_devices as device_list
    from .exceptions import DeviceError, PlatformIOError
    from .config import get_config
    from .utils.logging_config import setup_logging, get_logger
# Initialize configuration and logging
config = get_config()
setup_logging(config.LOG_LEVEL)
logger = get_logger("app")

app = Flask(__name__)
app.config.from_object(config)

@app.route('/')
def home():
    """Home page displaying ESP devices"""
    try:
        logger.info("Loading home page with device list")
        # devices: list[Device] = device_list()
        """For Now using mock data"""
        devices: list[Device] = get_mock_data()
        return render_template('home.html', devices=devices)
    
    except (DeviceError, PlatformIOError) as e:
        logger.error(f"Device error on home page: {str(e)}")
        return render_template('home.html', devices=[], error=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error on home page: {str(e)}")
        return render_template('home.html', devices=[], error="Failed to load devices")

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get list of connected devices"""
    try:
        logger.info("Requesting device list")
        devices: list[Device] = device_list()
        json_devices = [device.to_dict() for device in devices]
        
        logger.info(f"Returning {len(json_devices)} devices")
        return jsonify({
            'success': True,
            'data': json_devices,
            'count': len(json_devices)
        })
    
    except (DeviceError, PlatformIOError) as e:
        logger.error(f"Device error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'type': 'device_error'
        }), 500
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'type': 'server_error'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'message': 'IoT Remote Lab server is running'
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'type': 'not_found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'type': 'server_error'
    }), 500

def main():
    logger.info(f"Starting IoT Remote Lab server on {config.HOST}:{config.PORT}")
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
if __name__ == '__main__':
    main()
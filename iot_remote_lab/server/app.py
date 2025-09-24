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
        return render_template('home_fixed.html', devices=[], error="Failed to load devices")
@app.route('/new')
def new_home():
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
        return render_template('home_new.html', devices=[], error="Failed to load devices")
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

@app.route('/devices')
def device_list_page():
    """Device list page"""
    try:
        logger.info("Loading device list page")
        # devices: list[Device] = device_list()
        """For Now using mock data"""
        devices: list[Device] = get_mock_data()
        return render_template('device_list.html', devices=devices)
    
    except (DeviceError, PlatformIOError) as e:
        logger.error(f"Device error on device list page: {str(e)}")
        return render_template('device_list.html', devices=[], error=str(e))
    
    except Exception as e:
        logger.error(f"Unexpected error on device list page: {str(e)}")
        return render_template('device_list.html', devices=[], error="Failed to load devices")

@app.route('/simulator')
def simulator():
    """ESP device simulator page"""
    try:
        logger.info("Loading simulator page")
        return render_template('simulator.html')
    
    except Exception as e:
        logger.error(f"Unexpected error on simulator page: {str(e)}")
        return render_template('simulator.html', error="Failed to load simulator")

@app.route('/programmer')
def programmer():
    """C++ code programmer page"""
    try:
        logger.info("Loading programmer page")
        return render_template('programmer.html')
    
    except Exception as e:
        logger.error(f"Unexpected error on programmer page: {str(e)}")
        return render_template('programmer.html', error="Failed to load programmer")

@app.route('/api/save_program', methods=['POST'])
def save_program():
    """Save C++ program to file system"""
    import os
    import json
    from datetime import datetime
    
    try:
        data = request.get_json()
        program_name = data.get('program_name', '').strip()
        code = data.get('code', '')
        
        if not program_name:
            return jsonify({
                'success': False,
                'error': 'Program name is required'
            }), 400
            
        if not code.strip():
            return jsonify({
                'success': False,
                'error': 'Code cannot be empty'
            }), 400
        
        # Create programs directory if it doesn't exist
        programs_dir = os.path.join(os.getcwd(), 'programs')
        if not os.path.exists(programs_dir):
            os.makedirs(programs_dir)
        
        # Create program-specific folder
        program_folder = os.path.join(programs_dir, program_name)
        if not os.path.exists(program_folder):
            os.makedirs(program_folder)
        
        # Save main.cpp file
        cpp_file_path = os.path.join(program_folder, 'main.cpp')
        with open(cpp_file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Create metadata file
        metadata = {
            'program_name': program_name,
            'created_at': datetime.now().isoformat(),
            'file_path': cpp_file_path,
            'description': data.get('description', '')
        }
        
        metadata_file_path = os.path.join(program_folder, 'metadata.json')
        with open(metadata_file_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Program '{program_name}' saved successfully to {program_folder}")
        
        return jsonify({
            'success': True,
            'message': f'Program "{program_name}" saved successfully',
            'file_path': cpp_file_path,
            'folder_path': program_folder
        })
    
    except Exception as e:
        logger.error(f"Error saving program: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to save program: {str(e)}'
        }), 500

@app.route('/api/load_program/<program_name>')
def load_program(program_name):
    """Load a saved C++ program"""
    import os
    import json
    
    try:
        programs_dir = os.path.join(os.getcwd(), 'programs')
        program_folder = os.path.join(programs_dir, program_name)
        
        if not os.path.exists(program_folder):
            return jsonify({
                'success': False,
                'error': 'Program not found'
            }), 404
        
        cpp_file_path = os.path.join(program_folder, 'main.cpp')
        metadata_file_path = os.path.join(program_folder, 'metadata.json')
        
        if not os.path.exists(cpp_file_path):
            return jsonify({
                'success': False,
                'error': 'Program file not found'
            }), 404
        
        # Load code
        with open(cpp_file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Load metadata if it exists
        metadata = {}
        if os.path.exists(metadata_file_path):
            with open(metadata_file_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        
        return jsonify({
            'success': True,
            'program_name': program_name,
            'code': code,
            'metadata': metadata
        })
    
    except Exception as e:
        logger.error(f"Error loading program: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to load program: {str(e)}'
        }), 500

@app.route('/api/list_programs')
def list_programs():
    """List all saved programs"""
    import os
    import json
    
    try:
        programs_dir = os.path.join(os.getcwd(), 'programs')
        
        if not os.path.exists(programs_dir):
            return jsonify({
                'success': True,
                'programs': []
            })
        
        programs = []
        for folder_name in os.listdir(programs_dir):
            folder_path = os.path.join(programs_dir, folder_name)
            if os.path.isdir(folder_path):
                cpp_file_path = os.path.join(folder_path, 'main.cpp')
                metadata_file_path = os.path.join(folder_path, 'metadata.json')
                
                if os.path.exists(cpp_file_path):
                    program_info = {
                        'name': folder_name,
                        'folder_path': folder_path
                    }
                    
                    # Load metadata if available
                    if os.path.exists(metadata_file_path):
                        try:
                            with open(metadata_file_path, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                                program_info.update(metadata)
                        except:
                            pass
                    
                    programs.append(program_info)
        
        return jsonify({
            'success': True,
            'programs': programs
        })
    
    except Exception as e:
        logger.error(f"Error listing programs: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to list programs: {str(e)}'
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
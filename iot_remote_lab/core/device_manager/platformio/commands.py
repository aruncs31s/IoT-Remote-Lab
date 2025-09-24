import subprocess
import json
try:
    from model import Device
except ImportError:
    from .model import Device

def _get_devices() -> list[dict[str, str]]:
    try:
        result = subprocess.run(
            ["platformio", "device", "list", "--json-output"],
            capture_output=True,
            text=True,
            check=True
        )
        # Parse JSON output
        devices_data = json.loads(result.stdout)
        return devices_data if isinstance(devices_data, list) else [devices_data]
    except subprocess.CalledProcessError as e:
        print(f"Error executing PlatformIO command: {e}")
        return []
    except FileNotFoundError:
        print("PlatformIO not found. Please ensure PlatformIO is installed and in PATH.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing PlatformIO JSON output: {e}")
        return []


def get_devices() -> list[Device]:
    devices: list[Device] = []
    output: list[dict[str, str]] = _get_devices()
    
    for device_data in output:
        try:
            # Extract device information from JSON data
            port = device_data.get("port", "")
            description = device_data.get("description", "")
            hwid = device_data.get("hardware_id", "")  # PlatformIO might use "hardware_id"
            
            if not hwid:  # Fallback to other possible keys
                hwid = device_data.get("hwid", "")
            
            devices.append(Device(
                port=port,
                description=description,
                hwid=hwid
            ))
        except Exception as e:
            print(f"Error processing device data {device_data}: {e}")
            continue
    
    return devices
    
if __name__ == "__main__":
    output = get_devices()
    print("PlatformIO Device List Output:")
    print(output)
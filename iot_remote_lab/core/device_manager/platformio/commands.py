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
    if output is None:
        return get_mock_data()
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


def get_mock_data() -> list[Device]:
    devices: list[Device] = []
    device_1 = Device(
        port="COM3",
        description="USB Serial Device",
        hwid="USB VID:PID=2341:0043 SER=12345 LOCATION",
    )
    device_2 = Device(
        port="/dev/ttyUSB0",
        description="FTDI USB Serial Device",
        hwid="USB VID:PID=0403:6001 SER=67890 LOCATION",
    ) 
    device_3 = Device(
        port="COM3",
        description="USB Serial Device",
        hwid="USB VID:PID=2341:0043 SER=12345 LOCATION",
    )
    devices.append(device_1)
    devices.append(device_2)
    devices.append(device_3)
    return devices

if __name__ == "__main__":
    output = get_devices()
    print("PlatformIO Device List Output:")
    print(output)
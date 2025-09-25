import json
import subprocess

try:
    from model import Device, DeviceState
except ImportError:
    from .model import Device, DeviceState


""" Singleton class to manage devices using PlatformIO commands """


class DeviceManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DeviceManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
        self._devices: list[Device] = []

    @property
    def devices(self) -> list[Device]:
        return self._devices

    @devices.setter
    def devices(self, value: list[Device]):
        self._devices = value

    def _get_devices(self) -> list[dict[str, str | int]]:
        try:
            result = subprocess.run(
                ["platformio", "device", "list", "--json-output"],
                capture_output=True,
                text=True,
                check=True,
            )
            # Parse JSON output
            devices_data = json.loads(result.stdout)
            return devices_data if isinstance(devices_data, list) else [devices_data]
        except subprocess.CalledProcessError as e:
            print(f"Error executing PlatformIO command: {e}")
            return []
        except FileNotFoundError:
            print(
                "PlatformIO not found. Please ensure PlatformIO is installed and in PATH."
            )
            result = []
            return result
        except json.JSONDecodeError as e:
            print(f"Error parsing PlatformIO JSON output: {e}")
            result = []
            return result

    def get_devices(self) -> list[Device]:

        output: list[dict[str, str | int]] = self._get_devices()
        if len(output) == 0:
            return self.get_mock_data()
        for device_data in output:
            try:
                # Extract device information from JSON data
                port: str = str(device_data.get("port", ""))
                description: str = str(device_data.get("description", ""))
                hwid: str = str(
                    # device_data.get("hardware_id", "")
                    device_data.get("hwid", "")
                )  # PlatformIO might use "hardware_id"

                # if not hwid:  # Fallback to other possible keys
                # hwid = device_data.get("hwid", "")

                self._devices.append(
                    Device(port=port, description=description, hwid=hwid)
                )
            except Exception as e:
                print(f"Error processing device data {device_data}: {e}")
                continue

        return self.devices

    def get_mock_data(self) -> list[Device]:
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

    def get_free_devices(self) -> list[Device]:
        return [
            device
            for device in self.devices
            if device.status == DeviceState.CONNECTED
            and device.status != DeviceState.BUSY
            or device.status != DeviceState.MONITORING
        ]

    def get_busy_devices(self) -> list[Device]:
        return [
            device
            for device in self.devices
            if device.status == DeviceState.BUSY
            or device.status == DeviceState.MONITORING
        ]

    def upload_firmware(
        self, env: str, port: str, build_path: str, device: Device
    ) -> tuple[bool, str]:
        if device.status != DeviceState.CONNECTED:
            return False, "device is not connected"
        if device.status == DeviceState.BUSY:
            return False, "device is busy"
        if device.status == DeviceState.MONITORING:
            return False, "device is monitoring"

        try:
            result = subprocess.run(
                [
                    "platformio",
                    "run",
                    # "-e",
                    # env,
                    "--target",
                    "upload",
                    f"--upload-port={port}",
                    f"--project-dir={build_path}",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            print(result.stdout)
            return True, ""
        except subprocess.CalledProcessError as e:
            print(f"Error executing PlatformIO upload command: {e}")
            print(e.stdout)
            print(e.stderr)
            return False, ""
        except FileNotFoundError:
            return (
                False,
                "PlatformIO not found. Please ensure PlatformIO is installed and in PATH.",
            )


if __name__ == "__main__":
    device_manager = DeviceManager()

    output = device_manager.get_devices()
    print("PlatformIO Device List Output:")
    print(output)

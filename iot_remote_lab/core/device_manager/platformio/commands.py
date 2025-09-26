import json
import subprocess

try:
    from model import Device, DeviceState
except ImportError:
    from .model import Device, DeviceState

import time

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
        self._mock_devices: list[Device] = []

    @property
    def devices(self) -> list[Device]:
        return self._devices

    @devices.setter
    def devices(self, value: list[Device]):
        self._devices = value

    def _get_connected_devices(self) -> list[dict[str, str | int]]:
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
        if len(self._devices) > 0:
            self._devices.clear()
        output: list[dict[str, str | int]] = self._get_connected_devices()

        for device_data in output:
            try:
                # Extract device information from JSON data
                port: str = str(device_data.get("port", ""))
                description: str = str(device_data.get("description", ""))
                hwid: str = str(device_data.get("hwid", ""))
                if not hwid.strip() or not description.strip() or len(hwid) < 5:
                    continue
                # Only append unique devices based on port
                if any(d.port == port for d in self._devices):
                    continue
                self._devices.append(
                    Device(port=port, description=description, hwid=hwid)
                )
            except Exception as e:
                print(f"Error processing device data {device_data}: {e}")
                continue

        return self.devices if len(self.devices) > 0 else self.get_mock_data()

    def get_mock_data(self) -> list[Device]:
        if len(self._mock_devices) > 0:
            return self._mock_devices

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
            port="COM4",
            description="USB Serial Device",
            hwid="USB VID:PID=2341:0043 SER=12345 LOCATION",
        )
        self._mock_devices.append(device_1)
        self._mock_devices.append(device_2)
        self._mock_devices.append(device_3)
        if len(self.devices) == 0:
            self.devices = self._mock_devices
        return self._mock_devices

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
        self, env: str, build_path: str, device: Device
    ) -> tuple[bool, str]:
        if device.status != DeviceState.CONNECTED:
            return False, "device is not connected"
        if device.status == DeviceState.BUSY:
            return False, "device is busy"
        if device.status == DeviceState.MONITORING:
            return False, "device is monitoring"
        # port = device.port

        # Set status to busy
        device.status = DeviceState.BUSY

        proc = subprocess.Popen(
            ["platformio", "run", f"--project-dir={build_path}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # check in a loop
        while proc.poll() is None:  # poll() returns None if still running
            device.status = DeviceState.BUSY
            time.sleep(1)
        device.status = DeviceState.USING
        print("Process ended with code:", proc.returncode)
        return proc.returncode == 0, ""

    def get_device_by_port(self, port: str) -> Device:
        for device in self.get_devices():
            print(
                f"Device available: {id(device)} \nPORT: {device.port},\nDESC: {device.description},\nID: {device.hwid},\nNAME: {device.status.name}"
            )
        for device in self.devices:
            if device.port.lower().strip() == port.lower().strip():
                print(f"Found device on port {port}: {device}")
                return device
        return Device(
            port="N/A",
            description="No Device",
            hwid="N/A",
            # status=DeviceState.DISCONNECTED,
        )


if __name__ == "__main__":
    device_manager = DeviceManager()

    output = device_manager.get_devices()
    if len(output) == 0:
        output = device_manager.get_mock_data()

    print("PlatformIO Device List Output:")
    for device in output:
        print(
            f"Device on port: {device.port}, Description: {device.description}, HWID: {device.hwid}, Status: {device.status.name}"
        )

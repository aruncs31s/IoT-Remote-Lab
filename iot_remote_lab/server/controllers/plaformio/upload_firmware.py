import os

from ....core.device_manager.platformio.commands import DeviceManager


def upload_firmware(data: dict[str, any], dmg: DeviceManager) -> tuple[str, int, bool]:
    """Upload firmware to a device"""
    # try:

    program_name = data.get("program_name")
    if not isinstance(program_name, str):
        return ("Program name must be a string", 404, False)

    device: dict[str, str] = data.get("device", {})
    if not isinstance(device, dict) or "port" not in device:
        return ("Device information with valid port is required", 404, False)

    port: str = device.get("port").strip()

    print("device is", port)

    # TODO: make sure that we get the same device object

    device_obj = dmg.get_device_by_port(port.strip())
    print("device obj is", device_obj, " ids", id(device_obj))

    path = os.path.join(os.getcwd(), "programs", program_name)
    if not os.path.exists(path):
        return (f"Program {program_name} does not exist", 404, False)

    status, err = dmg.upload_firmware(device=device_obj, build_path=path, env="")
    if err != "" or not status:
        return (err, 500, False)
    print(status, err)
    print("path is", path)

    return ("Firmware upload initiated", 200, True)

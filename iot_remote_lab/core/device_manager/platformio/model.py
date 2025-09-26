"""This Will Handle all the data models"""

from enum import Enum


class DeviceState(Enum):
    """When the device is just connected"""

    CONNECTED = "connected"
    """When a user is using the device"""
    USING = "using"
    """When the device is disconnected"""
    DISCONNECTED = "disconnected"
    """When the device is in unknown state"""
    UNKNOWN = "unknown"
    """When the device is busy doing something"""
    BUSY = "busy"
    """When the user is monitoring serial output"""
    MONITORING = "monitoring"


class Device:
    _count = 0

    def __init__(self, port: str, description: str, hwid: str):
        self._port = port
        self._description = description
        self._hwid = hwid
        Device._count += 1
        self._status: DeviceState = DeviceState.CONNECTED

    @property
    def status(self) -> DeviceState:
        return self._status

    @status.setter
    def status(self, value: DeviceState):
        self._status = value

    @classmethod
    def get_count(cls):
        return cls._count

    @property
    def port(self) -> str:
        return self._port

    @port.setter
    def port(self, value: str):
        self._port = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def hwid(self):
        return self._hwid

    @hwid.setter
    def hwid(self, value):
        self._hwid = value

    def to_dict(self) -> dict:
        return {
            "port": self.port,
            "description": self.description,
            "hwid": self.hwid,
            "name": "ESP8266",
            "status": self.status.value,
        }

    def __repr__(self):
        return f"Device(port={self.port}, description={self.description}, hwid={self.hwid})"

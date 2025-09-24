"""This Will Handle all the data models"""


class Device:
    _count = 0
    def __init__(self, port: str, description: str, hwid: str):
        self._port = port
        self._description = description
        self._hwid = hwid
        Device._count += 1
    
    @classmethod
    def get_count(cls):
        return cls._count

    @property
    def port(self):
        return self._port
    
    @port.setter 
    def port(self, value):
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
            "hwid": self.hwid
        }
    def __repr__(self):
        return f"Device(port={self.port}, description={self.description}, hwid={self.hwid})"  
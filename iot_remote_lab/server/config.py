"""
Configuration management for IoT Remote Lab server
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Application configuration"""
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 5000
    LOG_LEVEL: str = "INFO"
    PLATFORMIO_TIMEOUT: int = 30
    MAX_DEVICE_SCAN_ATTEMPTS: int = 3
    DEVICE_SCAN_INTERVAL: int = 5


def get_config() -> Config:
    """Get configuration from environment variables or defaults"""
    return Config(
        DEBUG=os.getenv("DEBUG", "true").lower() == "true",
        HOST=os.getenv("HOST", "127.0.0.1"),
        PORT=int(os.getenv("PORT", "5000")),
        LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
        PLATFORMIO_TIMEOUT=int(os.getenv("PLATFORMIO_TIMEOUT", "30")),
        MAX_DEVICE_SCAN_ATTEMPTS=int(os.getenv("MAX_DEVICE_SCAN_ATTEMPTS", "3")),
        DEVICE_SCAN_INTERVAL=int(os.getenv("DEVICE_SCAN_INTERVAL", "5"))
    )
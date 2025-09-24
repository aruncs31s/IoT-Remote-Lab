# IoT Remote Lab

A Flask-based web application for managing IoT devices through PlatformIO.

## Project Structure

```
IoT-Remote-Lab/
├── server/
│   └── src/
│       ├── app.py                 # Main Flask application
│       ├── config.py              # Configuration management
│       ├── exceptions.py          # Custom exceptions
│       ├── controllers/
│       │   ├── __init__.py
│       │   └── platformio_helper/
│       │       ├── __init__.py    # Module exports
│       │       ├── __main__.py    # CLI interface
│       │       ├── devices.py     # Device management classes
│       │       └── pio_helper.py  # PlatformIO interface
│       └── utils/
│           ├── __init__.py
│           └── logging_config.py  # Logging configuration
├── requirements.txt               # Python dependencies
└── README.md                     # This file
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Server

```bash
cd server/src
python app.py
```

### API Endpoints

- `GET /api/devices` - Get list of connected devices
- `GET /api/health` - Health check endpoint

### CLI Interface

```bash
cd server/src/controllers
python -m platformio_helper
```

## Configuration

Environment variables:
- `DEBUG`: Enable debug mode (default: true)
- `HOST`: Server host (default: 127.0.0.1)
- `PORT`: Server port (default: 5000)
- `LOG_LEVEL`: Logging level (default: INFO)
- `PLATFORMIO_TIMEOUT`: PlatformIO command timeout (default: 30)

## Architecture

The application follows a modular architecture with:

1. **Separation of Concerns**: Device management, configuration, and web interface are separate modules
2. **Error Handling**: Custom exceptions with proper error responses
3. **Logging**: Structured logging throughout the application
4. **Configuration Management**: Environment-based configuration
5. **Type Hints**: Full type annotations for better code quality

## Scalability Considerations

1. **Modular Design**: Easy to add new device types and controllers
2. **Configuration Management**: Environment-based configuration for different deployments
3. **Error Handling**: Proper exception hierarchy for different error types
4. **Logging**: Structured logging for monitoring and debugging
5. **API Design**: RESTful API design for easy integration
6. **Extensibility**: Easy to add new endpoints and functionality

## Future Enhancements

1. Database integration for device persistence
2. Real-time device monitoring with WebSockets
3. Device control and programming capabilities
4. Authentication and authorization
5. Docker containerization
6. Unit and integration tests
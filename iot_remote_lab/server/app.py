from flask import Flask

try:
    from config import get_config
    from utils.logging_config import get_logger, setup_logging
except ImportError:
    from .config import get_config
    from .utils.logging_config import get_logger, setup_logging

# Import APIs
from .api import api_bp
# Import Pages
from .pages import pages_bp

# Initialize configuration and logging
config = get_config()
setup_logging(config.LOG_LEVEL)
logger = get_logger("app")

app = Flask(__name__)
app.config.from_object(config)

# Register blueprints
app.register_blueprint(pages_bp)
app.register_blueprint(api_bp)


def main_server():
    logger.info(f"Starting IoT Remote Lab server on {config.HOST}:{config.PORT}")
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)

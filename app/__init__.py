"""Flask application factory."""
import os
from flask import Flask
from config import config


def create_app(config_name='default'):
    """Create and configure the Flask application."""
    # Set template and static folders relative to project root
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    app.config.from_object(config[config_name])
    
    # Register blueprints
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint)
    
    return app

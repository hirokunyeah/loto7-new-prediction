"""Application configuration."""
import os


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    LOTO7_DATA_FILE = os.path.join(os.path.dirname(__file__), 'static', 'assets', 'loto7_data.json')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    ENV = 'development'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    ENV = 'production'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

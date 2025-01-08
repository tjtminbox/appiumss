import os

class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    SCREENSHOTS_DIR = 'screenshots'

class ProductionConfig(Config):
    ENV = 'production'
    SCREENSHOTS_DIR = '/var/www/screenshots'  # Production screenshots directory
    
class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True
    
class TestingConfig(Config):
    ENV = 'testing'
    TESTING = True
    DEBUG = True

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

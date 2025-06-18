import os
from dotenv import load_dotenv

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api

# Load .env variables
load_dotenv()

# Create extension objects
db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()

# Flask app instance
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Config classes
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    JSONIFY_PRETTYPRINT_REGULAR = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL', f"sqlite:///{os.path.join(basedir, 'dev.db')}")

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:///:memory:')

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///prod.db')

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}

# Use development config by default
env = os.getenv("FLASK_ENV", "development")
app.config.from_object(config_by_name[env])

# Initialize extensions with app
db.init_app(app)
ma.init_app(app)
migrate.init_app(app, db)

# 🔥 Only now import models (AFTER db is initialized)
from models import Tenants, Properties, Units, Leases, RentPayments, Expenses, MaintenanceRequests, Users

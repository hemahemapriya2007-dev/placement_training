# Service package
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import config


# Create SQLAlchemy object
db = SQLAlchemy()


def create_app(config_name="development"):

    # Create Flask application
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Connect SQLAlchemy with Flask
    db.init_app(app)

    # Home route
    @app.route("/")
    def home():
        return "Placement Training System is Running Successfully!"

    # Database connection test
    @app.route("/test-db")
    def test_db():

        try:
            with db.engine.connect() as connection:
                return "MySQL Database Connected Successfully!"

        except Exception as e:
            return f"MySQL Database Connection Failed: {e}"

    return app
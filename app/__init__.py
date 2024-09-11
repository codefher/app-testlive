# app/__init__.py
from flask import Flask
from .routes import configure_routes


def create_app():
    app = Flask(__name__)

    configure_routes(app, url_prefix="/api/")

    return app

# app/__init__.py
from flask import Flask
from .routes import configure_routes
# asegúrate de importar cualquier otra configuración o inicialización necesaria aquí

def create_app():
    app = Flask(__name__)
    # Configuraciones adicionales, como app.config['DEBUG'] = True, etc.
    
    configure_routes(app)  # Asegúrate de que esta función esté definida en routes.py

    return app

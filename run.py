from flask_cors import CORS

from app import create_app

app = create_app()
CORS(app)  # Habilita CORS en todas las rutas para todos los dominios

if __name__ == "__main__":
    app.run(
        host="0.0.0.0", port=5000, debug=True
    )  # Asegúrate de que Flask está escuchando en todas las interfaces

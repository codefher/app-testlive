# Utilizar una imagen base de Python con las librerías necesarias para compilar dlib
FROM python:3.9-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Instalar todas las dependencias necesarias para dlib, OpenCV y otras bibliotecas
RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-dev \
    libglib2.0-0 \
    cmake \
    build-essential \
    libopencv-dev \
    libpq-dev  # necesaria para psycopg2

# Copiar el archivo de requisitos e instalar las dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos de la aplicación
COPY . /app

# Exponer el puerto en el que Flask se ejecutará
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "run.py"]

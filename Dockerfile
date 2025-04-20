# Dockerfile

FROM python:3.13-slim

# Establece variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV IS_DOCKER=true

# Dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos necesarios
COPY requirements.txt /app/

# Instalar las dependencias del proyecto
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia todo el proyecto al contenedor
COPY . /app/

# Ejecutar el servidor de la app con Gunicorn
CMD ["gunicorn", "daw_films.wsgi:application", "--bind", "0.0.0.0:8000"]

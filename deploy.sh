#!/bin/bash

echo "Levantando contenedores y construyendo..."
docker compose up -d --build

echo "Ejecutando collectstatic..."
docker compose exec web python manage.py collectstatic --noinput

echo "Ejecutando makemigrations..."
docker compose exec web python manage.py makemigrations

echo "Ejecutando migrate..."
docker compose exec web python manage.py migrate

echo "Listo!"

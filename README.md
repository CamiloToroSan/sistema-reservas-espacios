# Sistema de Reservas de Espacios

Aplicación web para gestión de reservas de aulas, laboratorios y salas institucionales.

## Stack

- Django 6.x
- PostgreSQL (producción) / SQLite (desarrollo)
- Bootstrap 5 + Chart.js
- Despliegue: Render

## Instalación

```bash
git clone https://github.com/[usuario]/sistema-reservas-espacios.git
cd sistema-reservas-espacios
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # luego edita .env con tu clave
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
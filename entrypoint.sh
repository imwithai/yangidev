#!/bin/bash
set -e

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Creating default admin user if not exists..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
import os

User = get_user_model()
admin_email = os.environ.get('ADMIN_EMAIL', 'admin@yangidev.uz')
admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin123')

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', admin_email, admin_pass)
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"

echo "Starting server..."
exec "$@"

#!/bin/bash

# Wait for database
echo "🔄 Waiting for database..."
python manage.py wait_for_db 2>/dev/null || echo "wait_for_db command not available"

# Apply database migrations
echo "🔄 Applying database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "🔄 Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', '1122334455')
    print('✅ Superuser created: admin/1122334455')
else:
    print('✅ Superuser already exists')
" 2>/dev/null || echo "Superuser creation skipped"

# Collect static files
echo "🔄 Collecting static files..."
python manage.py collectstatic --noinput

# Load test data if needed
echo "🔄 Loading test data..."
python manage.py seed_db 2>/dev/null || echo "Seed command not available"

# Warm cache
echo "🔄 Warming cache..."
python manage.py warm_cache 2>/dev/null || echo "Cache warming skipped"

# Start server
echo "🚀 Starting Django server..."
python manage.py runserver 0.0.0.0:8000
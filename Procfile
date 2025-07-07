release: python manage.py migrate && python manage.py collectstatic --noinput
web: gunicorn storefront.wsgi
worker: celery -A storefront worker




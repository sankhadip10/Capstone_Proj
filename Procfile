release: python manage.py migrate && python manage.py collectstatic --noinput && python manage.py warm_cache --clear-first
web: gunicorn storefront.wsgi --log-file -
worker: celery -A storefront worker --loglevel=info --concurrency=4
beat: celery -A storefront beat --loglevel=info




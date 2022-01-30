web: gunicorn app:manage.app
worker: celery worker --app=project.server.tasks.celery --loglevel=info

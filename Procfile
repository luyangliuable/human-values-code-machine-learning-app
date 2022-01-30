web: gunicorn app:manage
worker: celery worker --app=project.server.tasks.celery --loglevel=info

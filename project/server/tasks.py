import os
import time

from flask import jsonify, send_file

from celery import Celery

from project.machine_learning import machine_learning

celery = Celery(__name__)
celery.conf.broker_url = os.environ['REDIS_URL']
# celery.conf.celery_task_serializer = 'json'
celery.conf.result_backend = os.environ['REDIS_URL']
celery.config['UPLOAD_FOLDER'] = 'project/server/upload'



@celery.task(name="create_task")
def create_task(info):
    print(info)
    file = info['file']
    column = info['column']
    result = machine_learning.background_file_labeler(file, column)
    return result, 200


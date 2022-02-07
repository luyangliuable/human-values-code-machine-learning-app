import os
import time

from flask import jsonify, send_file

from celery import Celery

from project.machine_learning import app as machine_learning

celery = Celery(__name__)
celery.conf.broker_url = os.environ['REDIS_URL']
celery.conf.result_backend = os.environ['REDIS_URL']


@celery.task(name="create_task")
def create_task(info):
    type = info['type']
    if type == 'label':
        file = info['file']
        column = info['column']
        result = machine_learning.background_file_labeler(file, column)
        return result, 200


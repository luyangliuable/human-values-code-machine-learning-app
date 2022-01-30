import os
import time

from flask import jsonify, send_file

from celery import Celery

from project.machine_learning import app as machine_learning

celery = Celery(__name__)
celery.conf.broker_url = os.environ["redis://:pbde7018282c5cc3afc21b12012e4eb52ee56eda5dd96c819113b3e7694dabe13@ec2-35-168-186-135.compute-1.amazonaws.com:27890"]
celery.conf.celery_task_serializer = 'json'
celery.conf.result_backend = os.environ["redis://:pbde7018282c5cc3afc21b12012e4eb52ee56eda5dd96c819113b3e7694dabe13@ec2-35-168-186-135.compute-1.amazonaws.com:27890"]


@celery.task(name="create_task")
def create_task(info):
    print(info)
    file = info['file']
    column = info['column']
    result = machine_learning.background_file_labeler(file, column)
    return result, 200


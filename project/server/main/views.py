# project/server/main/views.py
import os
import tempfile
import struct
import pickle
import zlib
import numpy as np
from collections import Counter
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import redis
from redis import Redis
from flask import render_template, Blueprint, jsonify, request, Response, send_file, redirect, url_for
from celery.result import AsyncResult
from project.server.tasks import create_task
from project.machine_learning import app as machine_learning
main_blueprint = Blueprint("main", __name__) #, static_folder='static')

matplotlib.use('Agg')

# celery.conf.result_backend = os.environ['REDIS_URL']
r = Redis.from_url(os.environ['REDIS_URL'])


def store_data(request, column: str):
    r.flushdb()
    file = request.files.get('file')
    df = pd.read_csv(file)
    data = df[[ column, 'language' ]]
    r.set(column, zlib.compress( pickle.dumps(df)))
    return column


@main_blueprint.route('/label', methods=["GET", "POST"])
def label():

    if len(request.form) > 0:
        comment = request.form['comment']
        res = machine_learning.label(comment)

    return render_template("main.html", result=res)


@main_blueprint.route("/file_labeler", methods=["POST"])
def file_labeler():
    machine_learning.file_labeler()
    return render_template("main.html", result="Getting result...")


@main_blueprint.route("/repo", methods=["POST"])
def repo():
    res = machine_learning.repo()

    return render_template("main.html", result=res)


@main_blueprint.route("/", methods=["GET"])
def home():
    return render_template("main.html", result='')


@main_blueprint.route("/getChart/<dataname>")
def getChart(dataname):
    all_labels = ['security', 'self-direction', 'benevolence', 'conformity', 'stimulation', 'power', 'achievement', 'tradition', 'universalism', 'hedonism']

    print("getting chart")

    data = pickle.loads(zlib.decompress(r.get(dataname)))
    tmp = data['prediction'].values

    values = []
    for item in tmp:
        print(values)
        for val in item:
            print(val)
            if val == val:
                values.append(val)


    counter = Counter(values)

    amount = []
    labels = []
    for key, item in counter.items():
        labels.append(key)
        amount.append(item)

    for l in all_labels:
        if l not in labels:
            labels.append(l)
            amount.append(0)

    plt.rcParams["figure.figsize"] = [11.0, 3.50]
    plt.rcParams["figure.autolayout"] = True

    colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral']

    plt.bar(labels, amount, align='center')

    filename = 'lb3.jpg'
    with tempfile.TemporaryDirectory() as tmpdirname:
        plt.savefig((os.path.join(tmpdirname, filename)), bbox_inches='tight', pad_inches=.1)
        return send_file(os.path.join(tmpdirname, filename)), 200

    return 500


@main_blueprint.route("/getCSV/<data>")
def getCSV(data):
    data = pickle.loads(zlib.decompress(r.get(data)))
    with tempfile.TemporaryDirectory() as tmpdirname:
        data.to_csv(os.path.join( tmpdirname, 'file.csv' ))
        print('csv file successfully created', tmpdirname)

        return send_file(os.path.join( tmpdirname, 'file.csv' )), 200

    return 500


# @main_blueprint.route('/display/<filename>')
# def display_image(filename):
# 	return redirect(url_for('static', filename=filename), code=301)


@main_blueprint.route("/tasks", methods=["POST"])
def run_task():
    type = request.form.get('type')
    print("type is", type)
    if type == 'label':
        file = request.files.get('file')
        column = request.form.get('column')
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        filename = file.filename
        print('downloading file', column, filename)
        data_key= store_data(request, column)
        print('download complete')
        print('starting task to predict file')
        info = {'type': type, 'file': data_key, 'column': column }
        task = create_task.delay(info)
        print(task.id)
        return jsonify({"task_id": task.id}), 200
    if type == 'repo':
        repo_url = request.form.get('repo_url')
        branch = request.form.get('branch')
        info = {'type': type, 'repo_url': repo_url, 'branch': branch }
        task = create_task.delay(info)
        print(task.id)
        return jsonify({"task_id": task.id}), 200



@main_blueprint.route("/tasks/<task_id>", methods=["GET"])
def get_status(task_id):
    print('getting task id', task_id)
    task_result = AsyncResult(task_id)
    print(task_result)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return jsonify(result), 200

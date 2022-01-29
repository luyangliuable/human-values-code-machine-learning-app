# project/server/main/views.py
import os
from flask import render_template, Blueprint, jsonify, request, Response
from celery.result import AsyncResult
from project.server.tasks import create_task
from project.machine_learning import app as machine_learning
main_blueprint = Blueprint("main", __name__,)
upload_folder = './project/client/static/'

@main_blueprint.route('/label', methods=["GET", "POST"])
def label():

    if len(request.form) > 0:
        comment = request.form['comment']
        res = machine_learning.label(comment)

    return render_template("main.html", result=res)

@main_blueprint.route("/file_labeler", methods=["POST"])
def file_labeler():

    machine_learning.file_labeler()
    return render_template("main.html", result="getting result")

@main_blueprint.route("/repo", methods=["POST"])
def repo():
    res = machine_learning.repo()

    return render_template("main.html", result=res)

@main_blueprint.route("/", methods=["GET"])
def home():
    return render_template("main.html", result='')


@main_blueprint.route("/tasks", methods=["POST"])
def run_task():
    file = request.files.get('file')
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    print('downloading', file.filename)
    filename = file.filename
    file = request.files.get('file')
    filepath =  upload_folder + filename
    print('downloading file', filename)
    file.save(filepath)
    print('download complete')
    print('starting task to predict file')
    info = { 'file': filepath }
    print(info)
    task = create_task.delay(info)
    print(task.id)
    # return Response({"task_id": task.id}, status=201)
    return jsonify({"task_id": task.id}), 200


@main_blueprint.route("/tasks/<task_id>", methods=["GET"])
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return jsonify(result), 200

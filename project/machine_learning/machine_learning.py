import os
import time
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from celery import Celery
from flask import send_file, jsonify
from matplotlib.ticker import MaxNLocator
from collections import Counter
from itertools import chain
from project.machine_learning.src.model_trainer import model_trainer
from project.machine_learning.src.csv_file_modifier.modifier import csv_modifier
from project.machine_learning.src.preprocessor import preprocess as pre
from werkzeug.utils import secure_filename
from project.machine_learning.src import extractor
matplotlib.use('Agg')
download_folder = "project/server/upload"

model = model_trainer()
model.open_model('model_gbdt.pkl')
model.open_vocabulary('vectorizer.pkl')
model.open_binarizer('binarizer.pkl')

def process(comment):
  process = pre(dictionary_file='word.pkl')
  return process.process_comment(comment)


def plot_graph(counter, savedir):
  modifier = csv_modifier()
  all_labels = ['security', 'self-direction', 'benevolence', 'conformity', 'stimulation', 'power', 'achievement', 'tradition', 'universalism', 'hedonism']
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

  filename = modifier.find_next_filename('lb', savedir, 'jpg')

  plt.savefig(os.path.join(savedir, filename), bbox_inches='tight', pad_inches=.1)

  return filename


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def background_file_labeler(file, column: str):
  result = ""

  processed_files = []

  filename = file
  predicted_filename = 'predicted_file.csv'
  print("processing file: " + filename, 'in column', column)
  process = pre(file, column, dictionary_file='word.pkl')
  processed_files.append(process.create_new_processed_file(download_folder))

  print("predicting", processed_files)
  predicted_file = model.predict_file(['new_line', 'language'], processed_files[0], download_folder)

  processed_files = [os.path.join(download_folder, file) for file in processed_files]

  print("Skip: removing", processed_files)
  # remove_files(processed_files)

  print('interpreting', predicted_file)
  data = pd.read_csv(os.path.join(download_folder, predicted_file ))
  tmp = data['prediction'].values

  values = []
  for item in tmp:
    if item == item:
      values = values + item.strip().split(' ')

  print('Creating chart.')
  value_count = Counter(values)
  image = plot_graph(value_count, download_folder)

  res = ""
  for key, val in value_count.items():
    res = res + key + ': ' + str(val) + ' '

  frontend_download = "/static/"
  return {'count': res, 'image': image, 'file': predicted_file }

def file_labeler():
  if 'file' not in request.files:
      print("no file part")
      flash('No file part')
      return redirect(request.url)
  file = request.files.get('file')
  task = background_file_labeler(file)
  return True

def label(comment: str):
  comment = process(comment)[0]
  print("predictin comment: ", comment)
  item_to_predict = pd.DataFrame()
  item_to_predict['new_line'] = [ comment ]
  item_to_predict['language'] = ['python']
  results, binarizer = model.predict(item_to_predict)
  results = to_only_none(results)
  results = binarizer.inverse_transform(results)

  tmp = ""
  for result in results[0]:
    if tmp == "":
      tmp = result
    else:
      tmp = tmp + ", " + result

  results = tmp

  if results == 'none':
    results = 'There is no value mention.'
  return results

def to_only_none(input):
    res = []
    for i, item in enumerate(input):
        if item[4] == 1 or not np.any(item):
            x = [0] * len(item)
            x[4] = 1
            res.append(x)

        else:
            res.append(item)
    return np.array(res)

def repo():
  files = ""
  processed_files = []
  if len(request.form) > 0:
    repo = request.form['repo_url']
    branch = request.form['branch']
    try:
      files = extractor.get_comment_from_repo_using_all_languages(repo , branch, './')
      column = 'line'
      for file in files:
        print("processing file: " + file)
        process = pre(file, column)
        processed_files.append(process.create_new_processed_file())

      remove_files(files)
      print("predicting")
      result = model.predict_files(['new_line', 'language'], processed_files)
      remove_files(processed_files)
      download = send_file(result)
    except Exception as e:
      print(e)
  return download


def remove_files(files: list[str]) -> None:
  for file in files:
    os.remove(file)

# @app.route('/result')
# def reporter(result):
#     return str(result)

if __name__ == '__main__':
  app.run(debug=True)

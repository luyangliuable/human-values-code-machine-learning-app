import os
import time
# import git
from redis import Redis
import tempfile
import pickle
import zlib
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
from project.machine_learning.src import util
from project.machine_learning.src.csv_file_modifier.modifier import csv_modifier
from project.machine_learning.src.preprocessor import preprocess as pre
from project.machine_learning.src.duplicate_remover import comment_database as cdb
from werkzeug.utils import secure_filename
from project.machine_learning.src import extractor
matplotlib.use('Agg')

model = model_trainer()
model.open_model('model_gbdt.pkl')
model.open_vocabulary('vectorizer.pkl')
model.open_binarizer('binarizer.pkl')

# r = Redis("machine_learning_app_redis_1", 6379)
r = Redis.from_url(os.environ['REDIS_URL'])

def process(comment):
  process = pre(dictionary_file='word.pkl')
  return process.process_comment(comment)


def store_df(data, name) -> bool:
    r.set(name, zlib.compress( pickle.dumps(data)))
    print('sucessfully stored')
    return True


def plot_graph(counter, savedir):
  modifier = csv_modifier()

  # all_labels = ['security', 'self-direction', 'benevolence', 'conformity', 'stimulation', 'power', 'achievement', 'tradition', 'universalism', 'hedonism']

  print('counter is ', counter)

  labels, amount = util.label_counter(counter)

  print(labels)
  print(amount)

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

  download_folder = "project/server/"
  filename = file

  data = pickle.loads(zlib.decompress(r.get(column)))

  print("processing file: " + filename, 'in column', column)

  process = pre(file, column, dictionary_file='word.pkl')

  data['new_line'] = data[column].apply(lambda x: process.process_comment(x)[0])

  print("predicting", filename)

  prediction, binarizer = model.predict(data[['new_line', 'language']])


  prediction = binarizer.inverse_transform(prediction)

  print(prediction)

  data['prediction'] = prediction

  tmp = data['prediction'].values

  print('tmp is', tmp)

  values = []
  for item in tmp:
    for val in item:
      if val == val:
        values.append(val)


  print('Creating chart.')

  dataname = 'completed'

  store_df(data, dataname)

  value_count = Counter(values)

  # image = plot_graph(value_count, download_folder)

  res = ""
  for key, val in value_count.items():
    res = res + key + ': ' + str(val) + ' '

  return {"data": dataname, "count": res}

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

def repo(repo_url, branch):
    print("attempting to get from repo")
    repo = repo_url
    column = 'line'
    with tempfile.TemporaryDirectory() as tmpdirname:
      files = extractor.get_comment_from_repo_using_all_languages(repo , branch, tmpdirname)
      data = pd.DataFrame()
      for file in files:
        print(file)
        new_data = pd.read_csv(file)
        print(new_data.head)
        new_data = new_data.drop_duplicates(subset=['line'])
        new_data = new_data.drop_duplicates(subset=['location'])
        print(new_data.head)
        print(new_data.head)
        data = pd.concat([new_data, data])
        print("processing file: " + file)

      print(data.shape)
      print(data.head)


    processor = pre(file, column, dictionary_file='word.pkl')

    print('preprocessing...')
    data['new_line'] = data[column].apply(lambda x: processor.process_comment(x)[0])

    print("predicting...")
    prediction, binarizer = model.predict(data[['new_line', 'language']])
    prediction = binarizer.inverse_transform(prediction)

    data['prediction'] = prediction
    dataname = 'completed'

    store_df(data, dataname)

    tmp = data['prediction'].values
    values = []
    for item in tmp:
      for val in item:
        if val == val:
          values.append(val)

    value_count = Counter(values)

    res = ""
    for key, val in value_count.items():
      res = res + key + ': ' + str(val) + ' '

    # print(res)

    return {"data": dataname, "count": res}


def remove_files(files: list[str]) -> None:
  for file in files:
    os.remove(file)


if __name__ == '__main__':
  app.run(debug=True)

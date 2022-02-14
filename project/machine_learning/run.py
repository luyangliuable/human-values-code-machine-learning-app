import sys
from project.machine_learning.src.model_trainer import model_trainer
from project.machine_learning.src.preprocessor import preprocess as pre
from project.machine_learning src.import extractor as app
from project.machine_learning.src.duplicate_remover import comment_database as cdb
from project.machine_learning.src.keyword_filter import keyword_filter
from project.machine_learning.src.csv_file_modifier.modifier import csv_modifier as cm
###############################################################################
#               The run for the comment-extractor application              #
###############################################################################

length = len(sys.argv)

process = pre(dictionary_file='./src/word.pkl')

if length == 0:
  print('usage: run.py <command> <filename or repository')
  exit(0)

if length == 2 and sys.argv[1] in ('-h', '--help'):
  print('usage: \n run.py <command> <filename or repository')
  print('To get comments from directory: \n python3 run.py -d <root directory>')
  print('To get comments from repositories: \n python3 run.py -repo <repository link> <branch name> <depth>')

elif length >= 3:
    command1 = sys.argv[1]
    directory = sys.argv[2]
    if command1 == '-d':
      app.get_comment_from_path_using_all_languages(directory, './')
    elif command1 == '-repo':
      if length < 4:
        Exception("Not enough arguments")
      else:
        repo = sys.argv[2]
        branch = sys.argv[3]
        app.get_comment_from_repo_using_all_languages(repo , branch, './')
    elif command1 == "-process":
      leng = len(sys.argv)
      thing = sys.argv[2]
      for i in range(3, leng):
        print("processing file: " + sys.argv[i])
        process.open_csv_file(sys.argv[i])
        process.set_field_to_process(thing)
        process.create_new_processed_file()
    elif command1 == "-duplicate":
      leng = len(sys.argv)
      duplicated_files = []
      for i in range(2, len(sys.argv)):
        print("removing duplicates inside file: " + str(sys.argv[i]))
        comment_db = cdb(sys.argv[i])
        comment_db.remove_duplicates_in_database()
        comment_db.export_table_to_csv()
    elif command1 == '-auto':
      leng = len(sys.argv)
      duplicated_files = []
      for i in range(2, len(sys.argv)):
        print("removing duplicates inside file: " + str(sys.argv[i]))
        comment_db = cdb(sys.argv[i])
        comment_db.remove_duplicates_in_database()
        duplicated_files.append( comment_db.export_table_to_csv() )
      for each_file in duplicated_files:
        print("processing file: " + str(each_file))
        process = pre("./" + each_file, dictionary_file='./src/word.pkl')
        process.create_new_processed_file()

    elif command1 == "-comment":
      process = pre(dictionary_file='./src/word.pkl')
      stuff_to_process = {'line': sys.argv[2]}
      print(process.process_comment(stuff_to_process ))

    elif command1 == "-label":
      a = model_trainer()
      model = sys.argv[2]
      vectorizer = sys.argv[3]
      binarizer = sys.argv[4]
      file = sys.argv[5]
      print("model is", model)
      print("vectorizer is", vectorizer)
      print("binarizer is", binarizer)
      a.read_csv(file)
      a.open_model(model)
      a.open_vocabulary(vectorizer)
      a.open_binarizer(binarizer)
      a.predict_file([ 'new_line', 'language' ])
    elif command1 == "-filter":
      leng = len(sys.argv)
      for i in range(2, len(sys.argv)):
        print("filtering file: " + str(sys.argv[i]))
        filter = keyword_filter(sys.argv[i])
        filter.filter_csv_file(sys.argv[i])
    elif command1 == "-count":
      leng = len(sys.argv)
      count = 0
      for i in range(2, len(sys.argv)):
        modifier = cm(sys.argv[i])
        count += modifier.get_number_of_lines_in_file(sys.argv[i]) - 1
      print(count)
    elif command1 == "-extract":
      leng = len(sys.argv)
      language = sys.argv[2]
      print(language)
      count = 0
      for i in range(3, len(sys.argv)):
        print(sys.argv[i])
        get_every_line_from_file(sys.argv[i], languages["python"])


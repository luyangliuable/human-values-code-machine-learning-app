import pandas as pd
import os
import sys
import joblib as jlib
import numpy as np
import scipy.sparse as sp
import seaborn as seaborn
import sklearn
import nltk
import matplotlib.pyplot as plt
from sklearn.preprocessing import MultiLabelBinarizer
from nltk.stem import PorterStemmer
from collections import Counter
from sklearn.ensemble import AdaBoostClassifier, GradientBoostingClassifier
from project.machine_learning.src.preprocessor import preprocess as pre
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

DataFrame = pd.core.frame.DataFrame
DecisionTreeClassifier = sklearn.tree._classes.DecisionTreeClassifier
MultiLabelBinarizer = sklearn.preprocessing._label.MultiLabelBinarizer

class model_trainer:
    def __init__(self, csv_file: str=None) -> None:
        if csv_file is not None:
            self.csv_file = csv_file
        self.count_vector = CountVectorizer(ngram_range=(1,3), max_df=1000, encoding='utf-8', analyzer='word')


    def read_csv(self, csv_file: str=None, savedir: str='./') -> DataFrame:
        assert csv_file is not None, "No file to read"
        try:
            file_loc = os.path.join( savedir, csv_file )
            print("opening file", file_loc)
            self.csv_file = csv_file
            self.data = pd.read_csv(file_loc)
        except FileNotFoundError:
            print("FileNotFoundError: such file", csv_file)
        return self.data


    def open_model(self, model: str) -> DecisionTreeClassifier:
        try:
            print("opening model", model)
            self.model = jlib.load(model)
        except FileNotFoundError:
            print("FileNotFoundError: such file", model)
        return self.model

    def open_vocabulary(self, file: str) -> CountVectorizer:
        self.count_vector = jlib.load(file)
        return self.count_vector


    def open_binarizer(self, file: str) -> MultiLabelBinarizer:
        self.binarizer = jlib.load(file)
        print("binarizer file is:", file)
        return self.binarizer


    def stem(self, word: str) -> str:
        ps = PorterStemmer()
        return ps.stem(word)


    def inverse_transform(self, sparse_matrix):
        return self.count_vector.inverse_transform(sparse_matrix)


    def vectorizor_transform(self, sentence: str) -> str:
        return self.count_vector.transform(sentence)


    def binarizer_transform(self, sentence: str) -> str:
        return self.binarizer.transform(sentence)


    def predict(self, predictee: pd.core.frame.DataFrame) -> str:
        predictee = predictee.apply(lambda col: col.str.strip())
        print(predictee)
        predictee = predictee.apply(lambda x: self.count_vector.transform(x))
        predictee = sp.hstack(predictee)

        res = model_trainer.to_only_none(self.model.predict(predictee))

        return res, self.binarizer


    def predict_files(self, field_name_for_prediction: list, csv_file: list, savedir: str='./'):
        if len( csv_file ) != 0:
            data = pd.read_csv(csv_file[0])
            for i in range(1, len(csv_file)):
                print("predicting", csv_file[i])
                df = pd.read_csv(os.path.join(savedir, csv_file[i] ))
                data = model_trainer.concat_pd(data, df)
            predictions = self.predict(data[field_name_for_prediction])
            data['prediction'] = predictions
            filename = "predicted_data.csv"
            data.to_csv(os.path.join(savedir, filename ), index=False)
        return filename


    @staticmethod
    def concat_pd(first: DataFrame, second: DataFrame) -> DataFrame:
        return pd.concat([first, second], axis=0, ignore_index=True)


    def break_up_label(self, row) -> str:
        res = ""
        for each_label in row:
            print(each_label.strip())
            res = res + " " + each_label.strip()

        return res


    @staticmethod
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


    def predict_file(self, field_name_for_prediction: str, csv_file: str=None, savedir: str='./'):
        if csv_file is None:
            csv_file = self.csv_file

        print('reading', csv_file, 'for prediction')
        self.read_csv(csv_file, savedir)
        predictions, _ = self.predict(self.data[field_name_for_prediction])
        predictions = self.binarizer.inverse_transform(predictions)
        self.data['prediction'] = predictions
        self.data['prediction'] = self.data['prediction'].apply(lambda x: self.break_up_label(x))
        filename = "predicted_data_for_" + csv_file
        print(os.path.join(savedir, filename))
        self.data.to_csv(os.path.join(savedir, filename), index=False)
        return filename

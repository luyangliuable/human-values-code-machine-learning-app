import nltk
import os
import csv
import re
import joblib
import string
import chardet
import linecache
import pandas as pd
# import git
from typing import TypeVar, Generic, List, NewType
from nltk.metrics.distance  import edit_distance
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk import ngrams
from io import StringIO
from project.machine_learning.src.csv_file_modifier.modifier import csv_modifier as cm
from nltk.metrics.distance import edit_distance

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('words')
nltk.download('reuters')

from nltk.corpus import stopwords as sw
from nltk.corpus import reuters
from nltk.corpus import words

from nltk import FreqDist

T = TypeVar("T")

class preprocess():

    def __init__(self, csv_file: str=None, field_to_process: str='line', dictionary_file: str=None) -> None:
        self.field_to_process = field_to_process
        self.translate_table = dict((ord(char), None) for char in string.punctuation)
        print(dictionary_file)
        if dictionary_file !=  None:
            self.correct_words = joblib.load(dictionary_file)
        if csv_file is not None:
            self.open_csv_file(csv_file)

    def set_field_to_process(self, field_to_process: str='line'):
        self.field_to_process = field_to_process


    def open_csv_file(self, csv_file: str) -> None:
        self.filename = csv_file
        self.modified_csv_file = cm(csv_file)
        self.fieldname = self.modified_csv_file.get_og_filenames()
        self.add_field_to_fieldname("original_comment")
        self.add_field_to_fieldname("new_line")
        self.add_field_to_fieldname("trigram")
        self.add_field_to_fieldname("length")


    def correct_spelling(self, word:str, vocabulary: list, min_word_size: int=1) -> ( str, bool ):
        if len(word) > min_word_size:
            temp = [(edit_distance(word, w),w) for w in vocabulary if w[0]==word[0]]
            sorted_temp = sorted(temp, key = lambda val:val[0])
            if sorted_temp[0][0] <= 2:
                return sorted_temp[0][1], True
        return word, False


    def add_field_to_fieldname(self, new_field: str) -> None:
        if new_field not in self.fieldname:
            self.fieldname.append(new_field)


    def aux_split_word(self, word, vocabulary, common_words, res) -> bool:
        compound_word = False
        min_word_size = 5
        # spell_checked = self.correct_spelling(word, vocabulary, min_word_size)
        if word in vocabulary:
            res.append(word)
            compound_word = False
            return True
        # if spell_checked[1]:
        #     res.append(spell_checked[0])
        #     compound_word = False
        #     return True
        else:
            if word not in vocabulary and len(word) > min_word_size:
                for i in range(3, len(word) - 1):
                    left_tmp_word = word[:i]
                    right_tmp_word = word[i:]
                    if left_tmp_word in vocabulary  or right_tmp_word in vocabulary:

                        if right_tmp_word not in common_words:
                            len_before = len(res)
                            left = self.aux_split_word(left_tmp_word, vocabulary, common_words, res)
                            right = self.aux_split_word(right_tmp_word, vocabulary, common_words, res)
                            if left:
                                compound_word = True
                                return True
                            else:
                                res = res[:len_before]
            if not compound_word:
                res.append(word)
                return False


    def split_word(self, sentence, is_list: bool=True) -> list:

        sentence = sentence.lower()
        vocabulary = ['coma', 'mark', 'runner', 'software', 'fixme', 'todo', 'coordinator', 'onboarding', 'announcing', 'https', 'coord', 'beats', 'alives']
        correct_words = self.correct_words + vocabulary
        common = ['ability', 'lied', "ting", "able", "cant", "fish", "ed", "ing", "gated"]
        res = []
        sentence = sentence.strip()
        if not is_list:
            sentence = [ x.strip() for x in sentence.split(' ') ]

        for word in sentence:
            self.aux_split_word(word,correct_words, common, res)
        if is_list == False:
            tmp = ""
            for word in res:
                tmp = tmp + " " + word

            return tmp


        return res

    def process_out_noise2(self, input: str) -> str:
        max_word_length = 18
        output = re.sub(r'\d+', 'number', input)
        w = re.findall(r'\w+', output)
        res = ""

        for word in w:
            if len(word) <= max_word_length:
                res += " " + word

        if output != '' and len(output) <= max_word_length:
            return output
        return res


    def replace_sym_with_space(self, sentence: str) -> str:
        symbols = ".()_-,\"'"
        rep = dict((re.escape(k), " ") for k in symbols)
        pattern = re.compile("|".join(rep.keys()))
        text = pattern.sub(lambda m: rep[re.escape(m.group(0))], sentence)
        text = text.translate(self.translate_table)
        return text


    def tokenise(self, sentence: str) -> List[str]:
        return nltk.word_tokenize(sentence)


    def create_dist_file(self, base_file_name: str="word_frequency_dictionary") -> str:
        file_size = self.modified_csv_file.get_number_of_lines_in_file(self.filename)

        frequency_dictionary = {}
        for i in range(2, file_size):
            first_line = linecache.getline(self.filename, 1)
            other_line = linecache.getline(self.filename, i)
            f = StringIO(first_line + other_line)

            line = csv.DictReader(f)
            line = [single_line for single_line in line][0]

            freq_tri = FreqDist(self.process_comment(line)[1])

            for keyword in freq_tri:

                if keyword in frequency_dictionary:
                    frequency_dictionary[keyword] += freq_tri[keyword]
                else:
                    frequency_dictionary.update({keyword : freq_tri[keyword]})

        if frequency_dictionary:
            newfile = self.modified_csv_file.create_csv_file(None, base_file_name, "json")

            f = open(newfile, "a", encoding="utf-8")
            f.write(str(frequency_dictionary))

            return newfile

        return None


    @staticmethod
    def stem(word: str) -> str:
        ps = PorterStemmer()
        return ps.stem(word)


    @staticmethod
    def is_stopword(word: str) -> bool:
        stopwords = sw.words('english')
        return word in stopwords


    def process_comment(self, comment: str) -> List[T]:
        # source: https://stackoverflow.com/questions/15547409/how-to-get-rid-of-punctuation-using-nltk-tokenizer#15555162

        line = comment
        line = self.replace_sym_with_space(line)
        line = self.split_word(line, is_list=False)
        line = self.process_out_noise2(line)
        tokens = self.tokenise(line)

        res = ""
        res2 = []
        for word in tokens:
            word = word.lower()
            if not self.is_stopword(word):
                word = self.stem(word)
                if res != "":
                    res = res + " " + word
                else:
                    res = word
                res2.append(word)

        return res, res2


    def create_trigram(self, line: dict) -> List[T]:

        _, tokens = self.process_comment(line)

        trigram = []

        trigram.extend(list(ngrams(tokens, 3,pad_left=True, pad_right=True)))

        new_trigram = []

        for quadriplet in trigram:
            count = 0
            for word in quadriplet:
                if word is None:
                    count = 1
                else:
                    count = count or 0
            if count != 1:
                new_trigram.append(quadriplet)

        return new_trigram


    def create_new_processed_file(self, savedir) -> str:
        base_file_name = "preprocessed_comment_file"

        newfile = self.modified_csv_file.find_next_filename(base_file_name, savedir=savedir)

        file_size = self.modified_csv_file.get_number_of_lines_in_file(self.filename)

        df = pd.read_csv(self.filename)


        # new_features = {'line': tokens, 'new_line': new_line, 'trigram': trigram, 'length': len(tokens)}

        new_features = ['line', 'new_line', 'trigram', 'length']

        print(self.field_to_process)
        df['original_comment'] = df[self.field_to_process]

        df['new_line'] = df[self.field_to_process].apply(lambda x: self.process_comment(x)[0])


        df.to_csv(os.path.join(savedir, newfile), index=False)

        # for i in range(2, file_size):
        #     first_line = linecache.getline(self.filename, 1)
        #     other_line = linecache.getline(self.filename, i)

        #     f = StringIO(first_line + other_line)

        #     line = csv.DictReader(f)

        #     line = [single_line for single_line in line][0]

        #     line['original_comment'] = line[self.field_to_process]

        #     new_line, tokens = self.process_comment(line)

        #     trigram = self.create_trigram(line)

        #     new_features = {'line': tokens, 'new_line': new_line, 'trigram': trigram, 'length': len(tokens)}

        #     for feature in new_features:
        #         if feature not in [key for key in line] or feature == "new_line" or feature == 'line':
        #             line[feature] = new_features[feature]


        #     line['new_line'] = new_features['new_line']

        #     row = []
        #     columns = []

        #     for column_name in line:
        #         columns.append(column_name)
        #         row.append(line[column_name])

        #     if len(line[self.field_to_process]) >= 3:
        #         self.modified_csv_file.append_to_csv_file(self.fieldname, row, newfile)


        return newfile

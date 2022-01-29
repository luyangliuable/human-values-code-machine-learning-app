import os
import csv
import re
from io import StringIO
import json
import linecache
import tempfile
import chardet
import sys
import inspect
sys.path.append('../../')
from project.machine_learning.src.csv_file_modifier.modifier import csv_modifier
from project.machine_learning.src.preprocessor import preprocess
from typing import TypeVar, Generic, List, NewType

T = TypeVar("T")

class keyword_filter():
    allLines = []
    dictLocation = "./keyword-dictionaries/keywords.JSON"
    dictionary = ""

    # values = ['choosing own goals', 'freedom', 'creativity', 'independent', 'privacy', 'choice', 'curious', 'self respect', 'excitement', 'varied', 'daring', 'pleasure', 'self indulgent', 'enjoying', 'ambitious']


    def __init__(self, csvfile: str) -> None:
        self.modifier = csv_modifier(csvfile)
        self.fieldnames = csv_modifier.get_fieldnames_from_csv_file(csvfile)
        self.file = csvfile
        self.open_file()
        self.get_keywords()
        self.values = self.get_keys_from_json()
        self.fieldnames.append('value')
        self.fieldnames.append('category')
        self.fieldnames.append('keywords')
        self.fieldnames.append('description')


    def get_keys_from_json(self) -> dict:
        res = []

        for key in self.dictionary:
            res.append(key)

        return res


    def search_file(self, filename: str) -> str:
        return self.modifier.search_file(filename, "./")


    @classmethod
    def check_words_in_line(self, words: str, line: str) -> List[str]:
        filteredWords = []

        for word in words:
            filteredWords += re.findall("\\b" + word + "\\b", line, flags=re.IGNORECASE)

        res = []
        for string in filteredWords:
            if string != "":
                res.append(string)

        return res

    def get_line_word_size(self, line: str) -> int:
        number_of_words = len(re.findall(r'\w+', line))
        return number_of_words


    def get_number_of_lines_in_file(self, file: str):
        with open(file, 'rb') as fp:
            c_generator = keyword_filter._count_generator(fp.raw.read)
            count = sum(buffer.count(b'\n') for buffer in c_generator)
            return count + 1

    @staticmethod
    def _count_generator(reader):
        b = reader(1024 * 1024)
        while b:
            yield b
            b = reader(1024 * 1024)

    def filter_csv_file(self, filename: str) -> None:
        new_filtered_file = self.create_csv_file()
        file_size = self.get_number_of_lines_in_file(filename)

        for i in range(1, file_size):
            first_line = linecache.getline(filename, 1)
            other_line = linecache.getline(filename, i)
            f = StringIO(first_line + other_line)
            line = csv.DictReader(f)
            line = [single_line for single_line in line][0]

            dict_to_append = {}
            # line, values, categories, str(keywords), location, language, description
            # for every line file get the language location and check against the values ##
            for field in line:
                dict_to_append[field] = line[field]

            try:
                line = line['new_line']
            except:
                # print('getting new line instead of new_line')
                line = line['new line']

            keywords = []
            description = ""
            has_keyword = False
            values = []
            categories = []

            for value in self.values:
                category = self.dictionary[value]['category']
                synonyms = self.get_synonyms(value)
                antonyms = self.get_antonyms(value)
                synonyms_in_line = self.check_words_in_line(synonyms, line)
                antonyms_in_line = self.check_words_in_line(antonyms, line)

                if len(synonyms_in_line) > 0 and self.get_line_word_size(line) >= 3:
                    has_keyword = True
                    description = "conforms with value"
                    keywords = keywords + synonyms_in_line
                    values.append("obeys " + value.lower())
                    categories.append(category)

                if len(antonyms_in_line) > 0 and self.get_line_word_size(line) >= 3:
                    has_keyword = True
                    if description != "":
                        description += ", value violation"
                    else:
                        description = "value violation"
                    keywords = keywords + antonyms_in_line
                    values.append("violates " + value.lower())
                    categories.append(category)

                dict_to_append['category'] = categories
                dict_to_append['value'] = values
                dict_to_append['keywords'] = keywords
                dict_to_append['description'] = description

            if has_keyword:
                self.append_to_csv_file(dict_to_append, new_filtered_file)

    def get_synonyms(self, value: str) -> str:
        res = []
        synonyms = self.dictionary[value]["synonyms"]
        for synonym in synonyms:
            res.append(preprocess.stem(synonym))
        return res

    def get_antonyms(self, value: str) -> str:
        res = []
        antonyms = self.dictionary[value]["antonyms"]
        for antonym in antonyms:
            res.append(preprocess.stem(antonym))
        return res


    def get_all_lines(self) -> List[T]:
        return self.allLines

    def filter_list_of_files(self, list_of_files: List[T]) -> None:
        for file in list_of_files:
            self.filter_csv_file(file)


    def get_keywords(self) -> List[T]:
        with open(self.dictLocation, encoding="utf-8") as dictionaryFile:
            self.dictionary = json.load(dictionaryFile)


    @staticmethod
    def _get_all_file_in_dir(path: str) -> List[T]:
        list_of_files = []

        for root, dirs, files in os.walk(path):
            for file in files:
                list_of_files.append(os.path.join(root,file))

        return list_of_files


    def create_csv_file(self) -> str:
        counter = 0
        while True:
            filename = "filtered_commentfile" + str( counter ) + ".csv"
            if len(self.search_file(filename)) == 0:
                f = open(filename, "w")
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
                f.close()
                break

            counter += 1

        return filename

    def append_to_csv_file(self, appendage: list, filename: str) -> None:
        """
        keyword args
        lines_of_comment
        value
        category
        keywords
        location
        description
        filename
        """
        with open(filename, "a", encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=self.fieldnames)
            writer.writerows([appendage])
            file.close()


    def open_file(self) -> None:
        self.allLines = []
        with open(self.file, encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                self.allLines.append(line.strip("\n"))


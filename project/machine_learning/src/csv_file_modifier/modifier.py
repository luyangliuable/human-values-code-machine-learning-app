import nltk
import csv
import linecache
import chardet
import pandas as pd
import os
import inspect
import sys
# import git
from io import StringIO
from typing import TypeVar, Generic, List, NewType

T = TypeVar("T")

class csv_modifier():

    WILDCARD_IDENTIFIER = "*"

    def __init__(self, filename: str=None) -> None:
        if filename != None:
            self.open_file(filename)

    def get_fieldname(self):
        return self.fieldname

    def get_og_filenames(self) -> List[T]:
        return self.og_fieldnames

    def turn_list_into_fields(self, the_list: List[T], is_field: bool=False) -> str:
        if is_field:
            res = "("
            for i in range(len( the_list )):
                field = the_list[i]
                if i != len(the_list) - 1:
                    res+= "\"\"\"" + str(field) +"\"\"\", "
                else:
                    res += "\"\"\"" + str(field) + "\"\"\")"
        else:
            res = "("
            for i in range(len( the_list )):
                field = the_list[i]
                if i != len(the_list) - 1:
                    res+= "'" + str(field) +"', "
                else:
                    res += "'" + str(field) + "')"

        return res


    def append_to_csv_file(self, fields: List[T], values: List[T], filename: str ) -> None:
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

        row = {}

        if len(fields) != len(values):
            Exception("Field and value must be same size")

        for i in range(len(fields)):
            row.update({fields[i]: values[i]})

        with open(filename, "a", encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writerows([row])
        file.close()

    @staticmethod
    def get_fieldnames_from_csv_file(filename: str) -> List[T]:
        print(filename)
        directory_path = os.getcwd()
        print(directory_path)
        allfiles = os.listdir(directory_path)
        allfiles = os.listdir('project/server/upload')
        print(allfiles)
        data = pd.read_csv(os.path.join('project/server/upload', filename))
        print(data.iloc[0])
        print('data si', data.iloc[0])
        print(data.iloc[0])
        first_line = linecache.getline(filename, 1)
        f = StringIO(first_line)
        line = csv.reader(f, delimiter = ',')
        surrounded_fields = [single_line for single_line in line]
        line = surrounded_fields[0]
        return line


    @classmethod
    def search_file(cls, file_name: str, path: str, filetype: str='jpg') -> List[T]:
        """Search a root directory for a particular file

        Keyboard Arguments:
        file_name -- name of the file to search for
        path -- path from which to search the file
        """
        # print("Searching in path: " + path + " for " + file_name)
        res = []
        for root, dirs, files in os.walk(path):
            if file_name[0] == cls.WILDCARD_IDENTIFIER:
                for file in files:
                    same_format = check_file_is_same_format(file_name, file)
                    if same_format:
                        if root[-1] != "/" and file[0] != "/":
                            res.append(root + "/" + file)
                        else:
                            res.append(root + file)
            else:
                for file in files:
                    if file == file_name:
                        if root[-1] != "/" and file[0] != "/":
                            res.append(root + "/" + file)
                        else:
                            res.append(root + file)

                found = file.find(file_name)

                if found != -1:
                    break
        return res

    @staticmethod
    def check_file_is_same_format(file_one: List[T], file_two: List[T]) -> bool:
        """Checks if file1 and file2 are of the same format

        Keyword Arguments:
        file_one -- the first file in the comparison
        file_two -- the second file in the comparison
        """

        # Get the file format of first file ###########################################
        counter = 1
        first_fileformat = ""
        while file_one[-counter] != "." and counter < len(file_one):
            first_fileformat = first_fileformat + file_one[-counter]
            counter += 1

        # Get the file format of second file ###########################################
        counter = 1
        second_fileformat = ""
        while file_two[-counter] != "." and counter < len(file_two):
            second_fileformat = second_fileformat + file_two[-counter]
            counter += 1

        if second_fileformat == first_fileformat:
            return True

        return False


    def create_csv_file(self, fieldnames: List[T], base_file_name: str, savedir: str="./") -> str:
        save_loc = self.find_next_filename(base_file_name, savedir)

        with open(save_loc, "w") as f:
            if filetype == "csv":
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                f.close()

        return save_loc


    def find_next_filename(self, base_file_name, savedir: str='./', filetype: str='csv'):
        counter = 0

        while True:
            filename = base_file_name + str( counter ) + "." + filetype

            save_loc = os.path.join(savedir, filename)

            if len(self.search_file(filename, savedir)) == 0:
                return filename

            counter += 1


    def open_file(self, csv_file: str) -> None:
            fieldname = self.get_fieldnames_from_csv_file(csv_file)
            self.og_fieldnames = fieldname
            self.fieldname = self.turn_list_into_fields(fieldname)


    def get_number_of_lines_in_file(self, file: str):
        with open(file, 'rb') as fp:
            c_generator = self._count_generator(fp.raw.read)
            count = sum(buffer.count(b'\n') for buffer in c_generator)
            return count + 1


    @staticmethod
    def _count_generator(reader):
        b = reader(1024 * 1024)
        while b:
            yield b
            b = reader(1024 * 1024)


    def import_comments_from_csv_file(self, filename: str) -> None:
        pass

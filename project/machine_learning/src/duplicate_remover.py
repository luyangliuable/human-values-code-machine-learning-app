import sqlite3
import csv
import linecache
from io import StringIO
from typing import TypeVar, Generic, List, NewType
import os
import inspect
import sys
sys.path.append('../../')
import project.machine_learning.src.extractor as app

T = TypeVar("T")

class comment_database:
    tablename = 'comments'

    def __init__(self, csv_file: str=None):
        if csv_file != None:
            fieldname = self.get_fieldnames_from_csv_file(csv_file, 1)
            self.og_fieldnames = fieldname
            self.fieldname = self.turn_list_into_fields(fieldname, False)
        self.connection = sqlite3.connect('comments.db')
        self.cur = self.connection.cursor()
        try:
            self.execute("""drop table """ + self.tablename)
        except:
            pass
        self.execute("""create table """ + self.tablename + self.fieldname)
        if csv_file != None:
            self.import_comments_from_csv_file(csv_file)
        self.commit()


    def remove_duplicates_in_database(self):
        print(self.og_fieldnames[0])
        print(self.og_fieldnames[1])
        self.execute("""
            delete from """ + self.tablename + """
            where rowid not in (select min(rowid)
            from """ + self.tablename + """
            group by """ + self.og_fieldnames[0] + """)
            """)
        self.execute("""
            delete from """ + self.tablename + """
            where rowid not in (select min(rowid)
            from """ + self.tablename + """
            group by """ + self.og_fieldnames[1] + """)
            """)
        self.commit()

    def export_table_to_csv(self, savedir: str) -> str:
        filename = self.create_csv_file(self.og_fieldnames, savedir)
        values = self.get_fields()
        for value in values:
            self.append_to_csv_file(self.og_fieldnames, value, filename)

        return os.path.join(savedir, filename)


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

    def create_csv_file(self, fieldnames: List[T], savedir: str) -> str:
        # fieldnames = ['line', 'location', 'language', 'value', 'category', "keywords", "description"]
        counter = 0

        while True:
            filename = "removed_duplicates_commentfile" + str( counter ) + ".csv"
            if len(app.search_file(filename, savedir)) == 0:
                f = open(os.path.join(savedir, filename ), "w")
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                f.close()
                break

            counter += 1

        return filename


    def get_fieldnames_from_csv_file(self, filename: str, line: int) -> List[T]:
            first_line = linecache.getline(filename, 1)
            f = StringIO(first_line)
            line = csv.reader(f, delimiter = ',')
            line = [single_line for single_line in line][0]
            return line


    def get_number_of_lines_in_file(self, file: str):
        with open(file, 'rb') as fp:
            c_generator = comment_database._count_generator(fp.raw.read)
            count = sum(buffer.count(b'\n') for buffer in c_generator)
            return count + 1


    def import_comments_from_csv_file(self, filename: str) -> None:
        file_size = self.get_number_of_lines_in_file(filename)

        for i in range(2, file_size):
            first_line = linecache.getline(filename, 1)
            other_line = linecache.getline(filename, i)
            f = StringIO(first_line + other_line)
            line = csv.DictReader(f)
            line = [single_line for single_line in line][0]
            for key in line:
                # if isinstance(line, str):
                line[key] = line[key].replace("'","''")
            list_of_values = []

            for key in line:
                list_of_values.append(line[key])

            self.insert_line(list_of_values)


    def remove_duplicate_in_list_of_files(self, list_of_files: List[T]) -> None:
        for file in list_of_files:
            print("getting: " + file)
            fieldname = self.get_fieldnames_from_csv_file(file, 1)
            self.og_fieldnames = fieldname
            self.fieldname = self.turn_list_into_fields(fieldname, False)
            self.execute("""drop table """ + self.tablename)
            self.execute("""create table """ + self.tablename + self.fieldname)
            self.import_comments_from_csv_file(file)
            self.remove_duplicates_in_database()
            self.export_table_to_csv()

    @staticmethod
    def _get_all_file_in_dir(path: str) -> List[T]:
        list_of_files = []

        for root, dirs, files in os.walk(path):
            for file in files:
                list_of_files.append(os.path.join(root,file))

        return list_of_files


    @staticmethod
    def _count_generator(reader):
        b = reader(1024 * 1024)
        while b:
            yield b
            b = reader(1024 * 1024)


    def get_fields(self) -> List[T]:
        res = []
        for row in self.cur.execute('SELECT * FROM ' + self.tablename):
            res.append(list(row))
        return res

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


    def insert_line(self, values: List[T]) -> None:
        values_to_be_inserted = self.turn_list_into_fields(values, False)
        query = """insert into """ + self.tablename + """ """ + self.fieldname + """ VALUES """ + values_to_be_inserted
        self.execute(query)


    def execute(self, query: str) -> None:
        self.cur.execute(query)
        self.commit()


    def commit(self) -> None:
        self.connection.commit()


    def close_connection(self):
        self.connection.close()

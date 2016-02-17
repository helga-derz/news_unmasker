# -*- coding: utf-8 -*-

import psycopg2
import logging
from parsers import interfax, kommersant, korrespondent, lenta, ria, rt, vlasti


class DbStructure:

    def __init__(self):
        self.id = ''
        self.name_parser = ''
        self.url = ''
        self.dwnl_time = ''
        self.dwnl_date = ''
        self.publ_time = ''
        self.publ_date = ''
        self.text = ''


class Psql:
    def __init__(self):
        self.conn = psycopg2.connect("dbname='news' user='postgres' host='localhost' password='postgres'")
        self.cur = self.conn.cursor()
        logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s %(message)s',
                            level=logging.INFO,
                            filename='psql_log.log',
                            filemode='a')

    parsers = {'interfax': interfax.Interfax(),
               'lenta': lenta.Lenta(),
               'kommersant': kommersant.Kommersant(),
               'korrespondent': korrespondent.Korrespondent(),  # недоработанный
               'ria': ria.Ria(),  # недоработанный
               'rt': rt.Rt(),
               'vlasti': vlasti.Vlasti()}  # кодировка иногда не та

    def close_connection(self):
        if self.conn:
            self.conn.close()
        logging.info('close connection')

    def insert(self, name_parser, since, to):
        parser_instance = self.parsers[name_parser]
        for feed in parser_instance.get_news(since, to):
            self.cur.execute(
                "INSERT INTO texts " +
                "(name_parser, download_date, download_time, text, publication_time, publication_date, url) " +
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (name_parser, feed.date, feed.time, feed.text, feed.publ_time, feed.publ_date, feed.url,))
        self.conn.commit()

    def create_table(self, name_table, dict_columns, pr_key):
        columns = ''
        for i in dict_columns:
            columns += i + ' ' + dict_columns[i]  # making a string from dict
            if i == pr_key:
                columns += ' PRIMARY KEY, '  # add primary key
            else:
                columns += ', '

        self.cur.execute('CREATE TABLE IF NOT EXISTS ' + name_table + ' (' + columns[:-2] + ');')
        self.conn.commit()

    def select(self, **kwargs):  # параметры для сортировки - словарь ('name_parser': '= lenta')

        where_list = []
        where_string = ' WHERE '

        if not kwargs:   # когда нет условий
            self.cur.execute("SELECT * FROM texts")
        else:
            for item, condition in kwargs.items():
                where_list.append(item + condition)

            where_string += ' AND '.join(where_list)
            self.cur.execute("SELECT * FROM texts" + where_string)

        rows = self.cur.fetchall()
        sorted_collection = []

        for row in rows:

            db_str = DbStructure()

            db_str.id = row[0]
            db_str.name_parser = row[1]
            db_str.url = row[2]
            db_str.dwnl_time = row[3]
            db_str.dwnl_date = row[4]
            db_str.publ_time = row[5]
            db_str.publ_date = row[6]
            db_str.text = row[7]

            sorted_collection.append(db_str)

        return sorted_collection


def adding_news(parser, since, to):
    db = Psql()

    db.insert(parser, since, to)

    db.close_connection()

# adding_news('lenta', '02.01.2015', '02.01.2015')

db = Psql()

coll = db.select(**{"name_parser": " = 'rt'", 'publication_date': " = '2014-12-31'"})

print coll[0].publ_time

db.close_connection()
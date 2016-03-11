# -*- coding: utf-8 -*-

import psycopg2
import logging
from parsers import interfax, kommersant, lenta, rt  # korrespondent, ria, vlasti


class ParsedArticleStructure:

    def __init__(self):
        self.id = ''
        self.name_parser = ''
        self.url = ''
        self.dwnl_time = ''
        self.dwnl_date = ''
        self.publ_time = ''
        self.publ_date = ''
        self.text = ''

    def split_row(self, row):
        self.id = row[0]
        self.name_parser = row[1]
        self.url = row[2]
        self.dwnl_time = row[3]
        self.dwnl_date = row[4]
        self.publ_time = row[5]
        self.publ_date = row[6]
        self.text = row[7]


class TrainCorpusStructure:

    def __init__(self):
        self.index_text = ''
        self.index_dir = None
        self.name = ''
        self.text = ''

    def split_row(self, row):
        self.index_text = row[0]
        self.index_dir = row[1]
        self.name = row[2]
        self.text = row[3]


class RelationStructure:

    def __init__(self):
        self.id = ''
        self.first_text = ''
        self.second_text = ''
        self.relation = ''

    def split_row(self, row):
        self.id = row[0]
        self.first_text = row[1]
        self.second_text = row[2]
        self.relation = row[3]


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
               # 'korrespondent': korrespondent.Korrespondent(),  # недоработанный
               # 'ria': ria.Ria(),  # недоработанный
               # 'vlasti': vlasti.Vlasti(),             # кодировка иногда не та
               'rt': rt.Rt()}

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

    def select_text(self, name_table, **kwargs):  # параметры для сортировки - словарь {'name_parser': '= lenta'}

        where_list = []
        where_string = ' WHERE '

        if not kwargs:   # когда нет условий
            self.cur.execute("SELECT * FROM " + name_table)
        else:
            for item, condition in kwargs.items():
                where_list.append(item + condition)

            where_string += ' AND '.join(where_list)
            self.cur.execute("SELECT * FROM " + name_table + where_string)

        rows = self.cur.fetchall()
        sorted_collection = []

        if name_table == 'texts':
            for row in rows:

                db_str = ParsedArticleStructure()
                db_str.split_row(row)

                sorted_collection.append(db_str)

        elif name_table == 'train_corpus':
            for row in rows:

                db_str = TrainCorpusStructure()
                db_str.split_row(row)

                sorted_collection.append(db_str)

        return sorted_collection

    def select_relations(self, name_table, **kwargs):

        where_list = []
        where_string = ' WHERE '

        if not kwargs:   # когда нет условий
            self.cur.execute("SELECT * FROM " + name_table)
        else:
            for item, condition in kwargs.items():
                where_list.append(item + condition)

            where_string += ' AND '.join(where_list)
            self.cur.execute("SELECT * FROM " + name_table + where_string)

        rows = self.cur.fetchall()
        sorted_collection = []

        for row in rows:
            db_str = RelationStructure()
            db_str.split_row(row)

            sorted_collection.append(db_str)

        return sorted_collection


def adding_news(parser, since, to):
    db = Psql()

    db.insert(parser, since, to)

    db.close_connection()


# adding_news('interfax', '17.06.2015', '16.06.2015')


'''
db = Psql()

coll = db.select(**{"name_parser": " = 'kommersant'", 'publication_date': " BETWEEN '2015-01-05' AND '2015-01-05'"})

for i in coll:
    print i.text
    print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'

db.close_connection()

'''
'''
db = Psql()

dates = [('21.06.2015', '15.08.2015'), ('16.08.2015', '15.10.2015'), ('16.10.2015', '31.12.2015')]

Done = False

for date in dates:

    while not Done:
        try:
            db.insert('rt', date[0], date[1])
            print 'done' + date[0] + ' - ' + date[1]
            Done = True
        except:
            print 'ouch ' + date[0] + ' - ' + date[1]

    Done = False
'''
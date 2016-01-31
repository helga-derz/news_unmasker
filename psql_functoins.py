# -*- coding: utf-8 -*-

import psycopg2
import logging
from parsers import interfax, kommersant, korrespondent, lenta, ria, rt, vlasti


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
               'korrespondent': korrespondent.Korrespondent(),          # недоработанный
               'ria': ria.Ria(),                                        # недоработанный
               'rt': rt.Rt(),
               'vlasti': vlasti.Vlasti()}                            # кодировка иногда не та

    def close_connection(self):
        if self.conn:
            self.conn.close()
        logging.info('close connection')

    def insert_news(self, name_parser, date, time, since, to):
        parser_instance = self.parsers[name_parser]
        for item in parser_instance.get_news(since, to):
            self.cur.execute("INSERT INTO texts " +
                        "(name_parser, download_date, download_time, text, publication_time, publication_date, url) " +
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (name_parser, date, time, item[0], item[1], item[2], item[3],))
        self.conn.commit()

    def create_table(self, name_table, dict_columns, pr_key):
        columns = ''
        for i in dict_columns:
            columns += i + ' ' + dict_columns[i]   # making a string from dict
            if i == pr_key:
                columns += ' PRIMARY KEY, '   # add primary key
            else:
                columns += ', '

        self.cur.execute('CREATE TABLE IF NOT EXISTS ' + name_table + ' (' + columns[:-2] + ');')
        self.conn.commit()

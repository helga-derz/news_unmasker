# -*- coding: utf-8 -*-

import psycopg2
import logging
from parsers import interfax, kommersant, korrespondent, lenta, ria, rt, vlasti

logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s %(message)s',
                    level=logging.INFO,
                    filename='psql_log.log',
                    filemode='w')

parsers = {'interfax': interfax.Interfax,
           'lenta': lenta.Lenta,
           'kommersant': kommersant.Kommersant,
           'korrespondent': korrespondent.Korrespondent,          # недоработанный
           'ria': ria.Ria,                                        # недоработанный
           'rt': rt.Rt,
           'vlasti': vlasti.Vlasti}


# Connect to a database
def connect():
    try:
        conn = psycopg2.connect("dbname='news' user='postgres' host='localhost' password='postgres'")
        logging.info('success to connect to the db')
        return conn
    except:
        logging.info('fail to connect to the db')
        return 'failed'


def close_connection(conn):
    conn.close()
    logging.info('close connection')
    return 'done'


def insert_news(cur, name_parser, date, time, since, to):
    parser_instance = parsers[name_parser]
    for item in parser_instance.get_news(since, to):
        cur.execute("INSERT INTO texts " +
                    "(name_parser, download_date, download_time, text, publication_time, publication_date, url) " +
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (name_parser, date, time, item[0], item[1], item[2], item[3],))

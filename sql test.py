# -*- coding: utf-8 -*-

import datetime
import psql_functoins as psql


now_time = datetime.datetime.now()  # Текущая дата со временем
date = now_time.strftime("%d.%m.%Y")  # форматируем дату
time = now_time.strftime("%H:%M")  # форматируем время


connection = psql.connect()
cur = connection.cursor()

psql.insert_news(cur, 'lenta', date, time, '01.01.2014', '01.01.2014')

connection.commit()
cur.close()
psql.close_connection(connection)

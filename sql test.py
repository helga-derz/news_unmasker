# -*- coding: utf-8 -*-

import datetime
from psql_functoins import Psql


now_time = datetime.datetime.now()  # Текущая дата со временем
date = now_time.strftime("%d.%m.%Y")  # форматируем дату
time = now_time.strftime("%H:%M")  # форматируем время

db = Psql()

db.insert_news('vlasti', date, time, '01.01.2014', '01.01.2014')

db.close_connection()

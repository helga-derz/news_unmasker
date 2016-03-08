# -*- coding: utf-8 -*-

import urllib2
import datetime
import logging


class Base:
    logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s %(message)s',
                        level=logging.ERROR,
                        filename='parser_log.log',
                        filemode='w')

    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Connection': 'close'}

    NAMES_OF_MONTHS = {'01': 'january',
                       '02': 'february',
                       '03': 'march',
                       '04': 'april',
                       '05': 'may',
                       '06': 'june',
                       '07': 'july',
                       '08': 'august',
                       '09': 'september',
                       '10': 'october',
                       '11': 'november',
                       '12': 'december'
                       }

    def __init__(self):
        pass

    # нужно для открытия конкретных статей
    def open_site(self, url, timeout):
        req = urllib2.Request(url, headers=self.hdr)
        page = urllib2.urlopen(req, timeout=timeout)

        return str(page.read())

    # возвращает список дат между первой и второй включительно
    def make_days_list(self, date1, date2):
        year1, year2 = int(date1.split('.')[2]), int(date2.split('.')[2])
        month1, month2 = int(date1.split('.')[1]), int(date2.split('.')[1])
        day1, day2 = int(date1.split('.')[0]), int(date2.split('.')[0])

        # когда нам нужны новости только за один день
        if date1 == date2:
            dates = [[date1.split('.')[2], date1.split('.')[1], date1.split('.')[0]]]

        # когда у нас период
        else:

            dates = []
            # разница между двумя датами
            delta = str(datetime.date(year2, month2, day2) - datetime.date(year1, month1, day1)).split(' ')[0]

            for i in range(int(delta) + 1):
                delta_temp = datetime.timedelta(days=i)
                date_temp = (datetime.date(year1, month1, day1) + delta_temp).strftime("%Y-%m-%d").split('-')
                dates.append(date_temp)

        # предыдущий день первого дня в списке (нужен для загрузки полной странички)
        day_out = (datetime.date(year1, month1, day1) - datetime.timedelta(days=1)).strftime("%Y-%m-%d").split('-')

        return dates, day_out

    # делим кортеж с датой на три числа
    def parsing_date(self, split_date):
        day = split_date[2]
        month = split_date[1]
        year = split_date[0]

        return day, month, year


class SimpleSites(Base):
    # проходим по спискам со статьями (метадата здесь)
    def scrolling_pages(self, page, date, main_site):
        list_daily_news = self.expr_for_article.findall(page)
        list_of_times = self.expr_for_time.findall(page)
        temp_list_news_metadata = []

        for index_news in xrange(len(list_daily_news)):
            try:
                text = self.get_text(list_daily_news[index_news])

                feed = NewsStructure()
                feed.text = text
                feed.publ_time = list_of_times[index_news]
                feed.publ_date = date
                feed.url = main_site + list_daily_news[index_news]

                temp_list_news_metadata.append(feed)
            except:
                logging.error(list_daily_news[index_news])

        return temp_list_news_metadata


class NewsStructure:
    def __init__(self):
        now_time = datetime.datetime.now()
        self.date = now_time.strftime("%d.%m.%Y")  # форматируем дату
        self.time = now_time.strftime("%H:%M")  # форматируем время
        self.publ_date = ''
        self.publ_time = ''
        self.text = ''
        self.url = ''

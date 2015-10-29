# -*- coding: utf-8 -*-

import re
import urllib2
import datetime

def make_days_list(date1, date2):              #возвращает список дат между первой и второй включительно

    year1, year2 = int(date1.split('.')[2]), int(date2.split('.')[2])
    month1, month2 = int(date1.split('.')[1]), int(date2.split('.')[1])
    day1, day2 = int(date1.split('.')[0]), int(date2.split('.')[0])

    dates = [[year1, month1, day1]]
    delta = str(datetime.date(year2, month2, day2) - datetime.date(year1, month1, day1)).split(' ')[0]  #разница между двумя датами

    for i in range(int(delta) + 1):

        delta_temp = datetime.timedelta(days=i)
        date_temp = (datetime.date(year1, month1, day1) + delta_temp).strftime("%Y-%m-%d").split('-')
        dates.append(date_temp)

    return dates


def open_site(url):

    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Connection': 'close'}

    req = urllib2.Request(url, headers=hdr)
    res = urllib2.urlopen(req)

    return str(res.read())


def get_news_ria(since, by):          #включая обе даты  ПОКА ВОЗВРАЩАЕТ ТОЛЬКО АДРЕСА СТРАНИЦ С ПОСЛЕДНИМИ 20 НОВОСТЯМИ ДНЯ

    list_daily_news = []
    for date in make_days_list(since, by):

        day = date[2]
        month = date[1]
        year = date[0]

        #общий сайт, где собраны все новости одного дня
        site_list_daily_news = open_site('http://ria.ru/world/' + str(year) + str(month) + str(day))

        #получаем ссылки на последние 20 новостей этого дня
        expr_for_list_daily_news = 'href="(/world/' + str(year) + str(month) + str(day) + '/[0-9]+\.html)"'
        expr_for_list_daily_news = re.compile(expr_for_list_daily_news)

        list_daily_news.extend(list(set(expr_for_list_daily_news.findall(site_list_daily_news))))

        '''
        #получаем ссылку, которая даст еще 20 новостей, еще 20 и т.д.
        expr_more_news = '<a href="" data-ajax="(/world/' + str(year) + str(month) + str(day) + '/more\.html\?id=[0-9]+&amp;date=' + str(year) + str(month) + str(day) + 'T[0-9]+&amp;onedayonly=1)" class'
        expr_more_news = re.compile(expr_more_news)

        site_more_news = expr_more_news.findall(site_list_daily_news)

        if site_more_news[0]:
            list_daily_news.extend(expr_for_list_daily_news.findall(open_site('http://ria.ru' + site_more_news[0])))
        '''

    return len(list_daily_news)

print get_news_ria('01.01.2015', '06.01.2015')
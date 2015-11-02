# -*- coding: utf-8 -*-

import re
import urllib2
import datetime
from contextlib import closing
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait


class Base:
    def __init__(self):
        pass

    def make_days_list(self, date1, date2):  # возвращает список дат между первой и второй включительно

        year1, year2 = int(date1.split('.')[2]), int(date2.split('.')[2])
        month1, month2 = int(date1.split('.')[1]), int(date2.split('.')[1])
        day1, day2 = int(date1.split('.')[0]), int(date2.split('.')[0])

        # когда нам нужны новости только за один день
        if date1 == date2:
            dates = [[year1, month1, day1]]

        # когда у нас период
        else:

            dates = [[year1, month1, day1]]
            # разница между двумя датами
            delta = str(datetime.date(year2, month2, day2) - datetime.date(year1, month1, day1)).split(' ')[0]

            for i in range(int(delta) + 1):
                delta_temp = datetime.timedelta(days=i)
                date_temp = (datetime.date(year1, month1, day1) + delta_temp).strftime("%Y-%m-%d").split('-')
                dates.append(date_temp)

        # предыдущий день первого дня в списке (нужен для загрузки полной странички)
        day_out = (datetime.date(year1, month1, day1) - datetime.timedelta(days=1)).strftime("%Y-%m-%d").split('-')

        return dates, day_out

    # нужно для открытия конкретных статей
    def open_site(self, url):
        hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Connection': 'close'}

        req = urllib2.Request(url, headers=hdr)
        res = urllib2.urlopen(req)

        return str(res.read())


class Ria(Base):

    # нужно для загрузки ВСЕХ новостей за день
    def loading_full_page(self, url, pr_year, pr_month, pr_day):

        with closing(Firefox()) as browser:
            browser.get(url)

            expr = pr_year + pr_month + pr_day + '/[0-9]+'

            # пока не появятся новости предыдущего дня
            while not re.compile(expr).findall(browser.page_source):
                button = browser.find_element_by_class_name('list_pagination_next')
                button.click()
                # wait for the page to load
                WebDriverWait(browser, timeout=15)

            page_source = browser.page_source

        return page_source

    # получаем ссылки на статьи с привязкой к дате
    def get_urls_news_ria(self, since, by):  # даты разделять точкой (после года не ставить)

        list_daily_news = []
        list_daily_news_metadata = []
        list_of_days, day_out = Base().make_days_list(since, by)[0], Base().make_days_list(since, by)[1]

        for index in range(len(list_of_days)):
            # нужная дата
            day = str(list_of_days[index][2])
            month = str(list_of_days[index][1])
            year = str(list_of_days[index][0])

            # предыдущая дата
            if index == 0:
                pr_day = str(day_out[2])
                pr_month = str(day_out[1])
                pr_year = str(day_out[0])
            else:
                pr_day = str(list_of_days[index - 1][2])
                pr_month = str(list_of_days[index - 1][1])
                pr_year = str(list_of_days[index - 1][0])

            # общий сайт, где собраны все новости одного дня
            site_list_daily_news = Ria().loading_full_page('http://ria.ru/world/' + year + month + day, pr_year, pr_month, pr_day)

            # получаем ссылки на новости этого дня
            expr_for_list_daily_news = 'href="(/world/' + year + month + day + '/[0-9]+\.html)"'
            expr_for_list_daily_news = re.compile(expr_for_list_daily_news)

            list_daily_news.extend(list(set(expr_for_list_daily_news.findall(site_list_daily_news))))

            # добавляем метадату
            for page in list_daily_news:
                list_daily_news_metadata.append([page, day + '.' + month + '.' + year])

        return list_daily_news_metadata

a = Ria()
for i in a.get_urls_news_ria('13.10.2015', '14.10.2015'):
    print i
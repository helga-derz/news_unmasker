# -*- coding: utf-8 -*-

import re
import urllib2
import datetime
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
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
    def scrolling_pages(self, page, date):

        list_daily_news = self.expr_for_article.findall(page)
        list_of_times = self.expr_for_time.findall(page)
        temp_list_news_metadata = []

        for index_news in xrange(len(list_daily_news)):
            try:
                text = self.get_text(list_daily_news[index_news])
                temp_list_news_metadata.append([text, list_of_times[index_news], date])
            except:
                logging.error(list_daily_news[index_news])

        return temp_list_news_metadata


# =========================================================================================================
#                Р И А - Н О В О С Т И (страницы иногда не догружаются, новости не все)
# =========================================================================================================
class Ria(Base):
    main_site = 'http://ria.ru'
    timeout = 50

    exprs_for_text = (
        re.compile('<h1.+</h1>'),
        re.compile('<div style="overflow.+[0-9]+</div>(.+)<div style'))

    expr_for_main_block = re.compile('>([А-Я]+\-*[А-Я]+\-*[А-Я]+,.+)</div><div id="facebook-userbar-article-end"',
                                     re.DOTALL)
    expr_for_parsing_main_block = re.compile('<p>.+</p>')
    # ненужные вставки в текст статьи
    expr_for_brief = re.compile('(<div id="inject_.+</div>)[А-я]+')

    # для метадаты   "article_header_time">12:03</span>14.10.2014</time>
    expr_for_date = re.compile(
        'datetime="([0-9]+-[0-9]+-[0-9]+)T[0-9]+:[0-9]+">')
    expr_for_time = re.compile(
        'datetime="[0-9]+-[0-9]+-[0-9]+T([0-9]+:[0-9]+)">')

    # нужно для загрузки ВСЕХ новостей за день
    def loading_full_page(self, url, day, month, year, block):

        self.browser.get(url)

        # регулярка для ссылок на нужный день
        expr_current_day = re.compile(
            '<h3 class="list_item_title"><a href="' + block + year + month + day + '/[0-9]+')

        # регулярка для ВСЕХ ссылок на статьи
        expr_other_day = re.compile('<h3 class="list_item_title"><a href="' + block + '[0-9]+/[0-9]+')

        # пока не появятся новости предыдущих дней
        while len(expr_current_day.findall(self.browser.page_source)) != 0 and \
                        expr_current_day.findall(self.browser.page_source)[-1] == \
                        expr_other_day.findall(self.browser.page_source)[-1]:

            try:
                button = self.browser.find_element_by_class_name('list_pagination_next')
                button.click()
                # wait for the page to load
                WebDriverWait(self.browser, timeout=self.timeout)

            except:
                self.browser.get(url)

        return self.browser.page_source

    # вытаскиваем текст из статьи
    def get_text(self, url):

        text = []
        article = self.open_site(self.main_site + url, self.timeout)

        for expr in self.exprs_for_text:
            text.extend(list(set(expr.findall(article))))

        main_block = self.expr_for_main_block.findall(article)
        text.extend(self.expr_for_parsing_main_block.findall(main_block[0]))

        parsed_article = ['\n\n'.join(text)]
        parsed_article.extend(self.get_metadata(article))

        return parsed_article

    # добавляем дату и время   (HH:MM, DD/MM/YYYY)
    def get_metadata(self, article):
        metadata = []

        metadata.append(self.expr_for_time.findall(article)[0])  # время
        metadata.append(self.expr_for_date.findall(article)[0])  # дата

        return metadata

    # получаем ссылки на статьи с привязкой к дате
    def get_news(self, since, by):  # даты разделять точкой (после года не ставить)

        browser = Firefox()

        blocks = ['/politics/', '/society/', '/economy/', '/world/', '/incidents/', '/sport/', '/studies/',
                  '/earth/', '/space/', '/optical_technologies/', '/culture/', '/religion_news/']

        list_all_parsed = []
        list_daily_news = []
        list_of_days, day_out = self.make_days_list(since, by)[0], self.make_days_list(since, by)[1]

        for index in xrange(len(list_of_days)):
            # нужная дата
            day = list_of_days[index][2]
            month = list_of_days[index][1]
            year = list_of_days[index][0]

            for block in blocks:
                # общий сайт, где собраны все новости одного дня
                site_list_daily_news = self.loading_full_page(self.main_site + block + year + month + day, day, month,
                                                              year, block)

                # получаем ссылки на новости этого дня
                expr_for_list_daily_news = re.compile('href="(' + block + year + month + day + '/[0-9]+\.html)"')

                list_daily_news.extend(list(set(expr_for_list_daily_news.findall(
                    site_list_daily_news))))  # сет потому, что некоторые ссылки находит дважды

        for url in list_daily_news:
            print url
            try:
                list_all_parsed.append(self.get_text(url))
            except:
                logging.error(list_daily_news[url])

        return list_all_parsed


# =========================================================================================================
#                К О М М Е Р С А Н Т
# =========================================================================================================
class Kommersant(SimpleSites):
    timeout = 50
    main_site = 'http://www.kommersant.ru'

    # регулярка для блока разметки с новостями(там ищем ссылки на статьи)
    expr_for_block_news = re.compile('<h3 class="subtitle"><a href="/news">.+<div class="col_group hide1 hide2">',
                                     re.DOTALL)

    # регулярка для ссылок на статьи
    expr_for_article = re.compile('<h3 class="article_subheader"><a href="(/news/[0-9]+)">')

    # регулярка для заголовка
    expr_for_text = re.compile('<title>.+</title>')

    # регулярка для тела статьи
    expr_for_body = re.compile('<div id="divLetterBranding" class="article_text_wrapper">(.+)<!-- RSS Link -->',
                               re.DOTALL)

    # регулярка для времени
    expr_for_time = re.compile('">([0-9]+:[0-9]+)</a></time>')

    # получаем текст статьи
    def get_text(self, url):

        text = []
        article = self.open_site(self.main_site + url, self.timeout).decode('cp1251').encode('utf-8')

        text.extend(self.expr_for_text.findall(article))
        text.extend(self.expr_for_body.findall(article))

        return '\n'.join(text)

    def get_news(self, since, by):

        list_of_days = self.make_days_list(since, by)[0]
        list_daily_news_with_metadata = []

        for index in range(len(list_of_days)):
            # нужная дата
            day, month, year = self.parsing_date(list_of_days[index])
            date = list_of_days[index][2] + '.' + list_of_days[index][1] + '.' + list_of_days[index][0]

            # общий сайт, где собраны все новости одного дня
            site_list_daily_news = 'http://www.kommersant.ru/archive/news/77/' + year + '-' + month + '-' + day

            # собираем статьи с первой страницы (на этом сайте страница всегда одна)
            page = self.open_site(site_list_daily_news, self.timeout)
            block_of_news = self.expr_for_block_news.findall(page)[0]
            list_daily_news_with_metadata.extend(self.scrolling_pages(block_of_news, date))

        return list_daily_news_with_metadata


# =========================================================================================================
#                К О Р Р Е С П О Н Д Е Н Т
# =========================================================================================================
class Korrespondent(SimpleSites):
    main_site = 'http://korrespondent.net'

    timeout = 50

    # регулярка для ссылок на статьи
    expr_for_article = re.compile('<h3><a href="([^"]+)">')

    # регулярка для заголовков
    expr_for_text = re.compile('<title>.+</title>'), re.compile('<h2>.+</h2>')

    # регулярка для тела статьи
    expr_for_body = re.compile('<p>.+</p>', re.DOTALL)

    # регулярка для времени
    expr_for_time = re.compile(', ([0-9]+:[0-9]+).', re.DOTALL)

    # получаем текст статьи
    def get_text(self, url):

        text = []
        article = self.open_site(url, self.timeout)

        for expr in self.expr_for_text:
            text.append(expr.findall(article)[0])

        text.extend(self.expr_for_body.findall(article))

        return '\n'.join(text)

    def get_news(self, since, by):

        list_of_days = self.make_days_list(since, by)[0]
        list_daily_news_with_metadata = []

        for index in range(len(list_of_days)):
            # нужная дата
            day, month, year = self.parsing_date(list_of_days[index])
            day = day.strip('0')
            month = self.NAMES_OF_MONTHS[month]

            date = list_of_days[index][2] + '.' + list_of_days[index][1] + '.' + list_of_days[index][0]

            # общий сайт, где собраны все новости одного дня
            site_list_daily_news = 'http://korrespondent.net/all/' + year + '/' + month + '/' + day

            # собираем статьи с первой страницы
            page = self.open_site(site_list_daily_news, self.timeout)
            list_daily_news_with_metadata.extend(self.scrolling_pages(page, date))

            # проходим по всем страницам этой даты
            page_number = 2
            while re.compile('href="(' + site_list_daily_news + '/p' + str(page_number) + '/)">').findall(page):
                page = self.open_site(site_list_daily_news + '/p' + str(page_number) + '/', self.timeout)

                list_daily_news_with_metadata.extend(self.scrolling_pages(page, date))

                page_number += 1

        return list_daily_news_with_metadata


# =========================================================================================================
#                И Н Т Е Р Ф А К С
# =========================================================================================================
class Interfax(SimpleSites):
    main_site = 'http://www.interfax.ru'

    timeout = 50

    # регулярка для ссылок на статьи
    expr_for_article = re.compile('</span><a href="(.+)" id=')

    # регулярка для заголовков
    expr_for_text = re.compile('<title>.+</title>'), re.compile('<h1 class="textMTitle" itemprop="headline">.+</h1>')

    # регулярка для тела статьи
    expr_for_body = re.compile('itemprop="articleBody">(.+\.)</p>', re.DOTALL)

    # регулярка для времени
    expr_for_time = re.compile('<div><span>([0-9]+:[0-9]+)</span><a')

    # получаем текст статьи
    def get_text(self, url):

        text = []
        article = self.open_site(self.main_site + url, self.timeout).decode('cp1251').encode('utf-8')

        for expr in self.expr_for_text:
            findings = expr.findall(article)
            if not findings == []:
                text.append(findings[0])

        text.extend(self.expr_for_body.findall(article))

        return '\n'.join(text)

    def get_news(self, since, by):

        list_of_days = self.make_days_list(since, by)[0]
        list_daily_news_with_metadata = []

        for index in range(len(list_of_days)):
            # нужная дата
            day, month, year = self.parsing_date(list_of_days[index])
            date = list_of_days[index][2] + '.' + list_of_days[index][1] + '.' + list_of_days[index][0]

            # общий сайт, где собраны все новости одного дня
            site_list_daily_news = 'http://www.interfax.ru/news/' + year + '/' + month + '/' + day

            # собираем статьи с первой страницы
            page = self.open_site(site_list_daily_news, self.timeout)
            list_daily_news_with_metadata.extend(self.scrolling_pages(page, date))

            # проходим по всем страницам этой даты
            page_number = 2
            while re.compile('/all/page_' + str(page_number)).findall(page):
                page = self.open_site(site_list_daily_news + '/all/page_' + str(page_number), self.timeout)

                list_daily_news_with_metadata.extend(self.scrolling_pages(page, date))

                page_number += 1

        return list_daily_news_with_metadata


# =========================================================================================================
#                R U S S I A N - R T
# =========================================================================================================
class Rt(SimpleSites):
    main_site = 'https://russian.rt.com'

    timeout = 50

    # регулярка для блока разметки с новостями(там ищем ссылки на статьи)
    expr_for_block_news = re.compile('class="list">(.+)<h2>Личное мнение</h2>',
                                     re.DOTALL)

    # регулярка для ссылок на статьи
    expr_for_article = re.compile('<h4>\s+<a href="(.+)"><strong>.+</strong></a>\s+</h4>')

    # регулярка для заголовков
    expr_for_text = re.compile('<title>.+</title>')

    # регулярка для тела статьи
    expr_for_body = re.compile('itemprop="headline description">(.+)</div>\s+<figure>', re.DOTALL), \
                    re.compile('itemprop="articleBody">(.+)<div class="orphus__hint"></div>', re.DOTALL)

    # регулярка для времени
    expr_for_time = re.compile(', ([0-9]+:[0-9]+)</aside>')

    # получаем текст статьи
    def get_text(self, url):

        text = []
        article = self.open_site(self.main_site + url, self.timeout)

        text.extend(self.expr_for_text.findall(article))
        for expr in self.expr_for_body:
            text.append(expr.findall(article)[0])

        return '\n'.join(text)

    def get_news(self, since, by):

        list_of_days = self.make_days_list(since, by)[0]
        list_daily_news_with_metadata = []

        for index in range(len(list_of_days)):
            # нужная дата
            day, month, year = self.parsing_date(list_of_days[index])
            date = list_of_days[index][2] + '.' + list_of_days[index][1] + '.' + list_of_days[index][0]

            # общий сайт, где собраны все новости одного дня
            site_list_daily_news = 'https://russian.rt.com/category/all/' + year + '-' + month + '-' + day

            # собираем статьи с первой страницы (на этом сайте страница всегда одна)
            page = self.open_site(site_list_daily_news, self.timeout)
            block_of_news = self.expr_for_block_news.findall(page)[0]
            list_daily_news_with_metadata.extend(self.scrolling_pages(block_of_news, date))

        return list_daily_news_with_metadata


a = Rt()
lt = a.get_news('22.11.2015', '23.11.2015')

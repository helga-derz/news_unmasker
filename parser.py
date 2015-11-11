# -*- coding: utf-8 -*-

import re
import urllib2
import datetime
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait


class Base:
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Connection': 'close'}

    timeout = 10

    def __init__(self):
        pass

    def make_days_list(self, date1, date2):  # возвращает список дат между первой и второй включительно

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

    # нужно для открытия конкретных статей
    def open_site(self, url):

        req = urllib2.Request(url, headers=self.hdr)
        res = urllib2.urlopen(req, timeout=self.timeout)

        return str(res.read())


# =========================================================================================================
#                Р И А - Н О В О С Т И
# =========================================================================================================
class Ria(Base):
    main_site = 'http://ria.ru'
    timeout = 50
    browser = Firefox()

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
        article = self.open_site(self.main_site + url)

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

        metadata.extend(self.expr_for_time.findall(article)[0])  # время
        metadata.extend(self.expr_for_date.findall(article)[0])  # дата

        return metadata

    # получаем ссылки на статьи с привязкой к дате
    def get_news(self, since, by):  # даты разделять точкой (после года не ставить)

        blocks = ['/politics/', '/society/', '/economy/', '/world/', '/incidents/', '/sport/', '/studies/',
                  '/earth/', '/space/', '/optical_technologies/', '/culture/', '/religion_news/']

        list_all_parsed = []
        list_daily_news = []
        list_of_days, day_out = self.make_days_list(since, by)[0], self.make_days_list(since, by)[1]

        for index in range(len(list_of_days)):
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

        cracked_urls = []
        for url in list_daily_news:
            print url
            try:
                list_all_parsed.append(self.get_text(url))
            except:
                cracked_urls.append(url)

        open('crack.txt', 'w').write('\n\n'.join(cracked_urls))
        return list_all_parsed


class Kommersant(Base):

    main_site = 'http://www.kommersant.ru'

    # регулярка для заголовка статьи
    expr_for_title = re.compile('<title>Ъ-Новости - .+</title>')
    # регулярка для тела статьи
    expr_for_text = re.compile('class="article_text_wrapper">(.+)<!-- RSS Link -->', re.DOTALL)

    def get_text(self, url):
        article = self.open_site(self.main_site + url)
#   СЮДАААААААААААААААААААААААААААААААААААА

    def get_news(self, since, by):

        list_of_days, day_out = self.make_days_list(since, by)[0], self.make_days_list(since, by)[1]
        list_daily_news = []
        list_all_parsed = []

        for index in range(len(list_of_days)):

            # нужная дата
            day = list_of_days[index][2]
            month = list_of_days[index][1]
            year = list_of_days[index][0]

            # общий сайт, где собраны все новости одного дня
            site_list_daily_news = 'http://www.kommersant.ru/archive/news/77/' + year + '-' + month + '-' + day

            # получаем блок со ссылками на новости этого дня
            expr_for_block_list_daily_news = re.compile('<section class="b-other_docs">.+</section>', re.DOTALL)
            block_of_news = expr_for_block_list_daily_news.findall(self.open_site(site_list_daily_news))

            # получаем ссылки на все новости этого дня
            expr_for_list_daily_news = re.compile('<h3 class="article_subheader"><a href="(/news/[0-9]+)">')

            list_daily_news.extend(expr_for_list_daily_news.findall(block_of_news[0]))

        for url in list_daily_news:
            print url
            list_all_parsed.append(self.get_text(url))

        return list_daily_news

a = Kommersant()
lt = a.get_news('14.01.2015', '14.01.2015')



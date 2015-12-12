# -*- coding: utf-8 -*-

from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait
import re
import parser.Base as Base
import logging


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

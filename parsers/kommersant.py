# -*- coding: utf-8 -*-

import re
import parser.SimpleSites as SimpleSites


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

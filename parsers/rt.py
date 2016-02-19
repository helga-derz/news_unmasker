# -*- coding: utf-8 -*-

import re
import parser


class Rt(parser.SimpleSites):
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
            list_daily_news_with_metadata.extend(self.scrolling_pages(block_of_news, date, self.main_site))

        return list_daily_news_with_metadata

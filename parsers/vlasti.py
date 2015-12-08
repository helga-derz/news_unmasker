# -*- coding: utf-8 -*-

import re
import parser.SimpleSites as SimpleSites


class Vlasti(SimpleSites):
    main_site = 'http://vlasti.net'

    timeout = 50

    # регулярка для блока разметки с новостями(там ищем ссылки на статьи)
    expr_for_block_news = re.compile('<div class="listdatanews">(.+)<!-- #end listdatanews-## -->',
                                     re.DOTALL)

    # регулярка для ссылок на статьи
    expr_for_article = re.compile('<div class="item">\s+<span>\s+<a href="(.+)" title=')

    # регулярка для заголовков
    expr_for_text = re.compile('<title>.+</title>'), re.compile('<h3><p>.+</p>\s</h3>')

    # регулярка для тела статьи
    expr_for_body = re.compile('<div class="newsimg">\s+<img src="[^А-я]+</div>(.+)<div class="clear"></div>\s+<div class="newsavtor">', re.DOTALL)

    # регулярка для времени
    expr_for_time = re.compile('<p class="rubrics"><strong>([0-9]+:[0-9]+)</strong>')

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
            date = list_of_days[index][2] + '.' + list_of_days[index][1] + '.' + list_of_days[index][0]

            # общий сайт, где собраны все новости одного дня
            site_list_daily_news = 'http://vlasti.net/news/date/' + year + '/' + month + '/' + day

            # собираем статьи с первой страницы
            page = self.open_site(site_list_daily_news, self.timeout)
            list_daily_news_with_metadata.extend(self.scrolling_pages(page, date))

            # проходим по всем страницам этой даты
            page_number = 2
            while re.compile('/page/' + str(page_number)).findall(page):
                page = self.open_site(site_list_daily_news + '/page/' + str(page_number), self.timeout)

                list_daily_news_with_metadata.extend(self.scrolling_pages(page, date))

                page_number += 1

        return list_daily_news_with_metadata


a = Vlasti()
lt = a.get_news('22.11.2015', '23.11.2015')
for i in lt:
    print i[0]
    print i[1]
    print i[2]
    print '\n\n\n'

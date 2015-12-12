# -*- coding: utf-8 -*-

import re
import parser.SimpleSites as SimpleSites


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

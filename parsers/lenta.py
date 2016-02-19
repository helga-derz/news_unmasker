# -*- coding: utf-8 -*-

import logging
import re
import parser


class Lenta(parser.Base):
    main_site = 'http://lenta.ru'

    timeout = 50
    rubrics = ['/rubrics/russia/', '/rubrics/world/', '/rubrics/economics/', '/rubrics/business/', '/rubrics/ussr/',
               '/rubrics/forces/', '/rubrics/science/', '/rubrics/sport/', '/rubrics/culture/', '/rubrics/media/',
               '/rubrics/style/', '/rubrics/travel/', '/rubrics/life/']

    # регулярка для ссылок на статьи
    expr_for_article = re.compile('<h3><a href="(/news/[^А-я]+)">')

    # регулярка для заголовка
    expr_for_text = re.compile('<title>.+</title>')

    # регулярка для тела статьи
    expr_for_body = re.compile('itemprop="articleBody">(.+)<section class="b-topic__socials">', re.DOTALL)

    # регулярка для "материалов по теме" в теле статьи (их нужно вырезать)
    expr_for_useless = re.compile('<aside class=.+</aside>'), \
            re.compile('<script.+</script>', re.DOTALL), \
            re.compile('<div class="eagleplayer".+8".>', re.DOTALL), \
            re.compile('<blockquote class=.+</blockquote>', re.DOTALL)

    # регулярка для времени
    expr_for_time = re.compile('pubdate=""> *([0-9]+:[0-9]+),')

    # получаем текст статьи (с метадатой)
    def get_text_metadata(self, url, date):

        text = []
        article = self.open_site(self.main_site + url, self.timeout)

        text.extend(self.expr_for_text.findall(article))
        body = self.expr_for_body.findall(article)[0]

        for expr in self.expr_for_useless:
            findings = expr.findall(body)
            for finding in findings:
                body = body.replace(finding, '')

        text.append(body)

        feed = parser.NewsStructure()
        feed.text = '\n'.join(text)
        feed.publ_date = date
        feed.publ_time = self.expr_for_time.findall(article)[0]
        feed.url = self.main_site + url

        return feed

    def get_news(self, since, by):

        list_of_days = self.make_days_list(since, by)[0]
        list_daily_news_with_metadata = []

        for index in range(len(list_of_days)):
            # нужная дата
            day, month, year = self.parsing_date(list_of_days[index])
            date = list_of_days[index][2] + '.' + list_of_days[index][1] + '.' + list_of_days[index][0]

            for rubric in self.rubrics:
                # общий сайт, где собраны все новости одного дня
                site_list_daily_news = self.main_site + rubric + year + '/' + month + '/' + day

                # собираем статьи с первой страницы
                page = self.open_site(site_list_daily_news, self.timeout)
                list_daily_news = self.expr_for_article.findall(page)

                for url in list_daily_news:
                    try:
                        list_daily_news_with_metadata.append(self.get_text_metadata(url, date))
                    except:
                        logging.error(url)

        return list_daily_news_with_metadata

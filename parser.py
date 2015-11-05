# -*- coding: utf-8 -*-

import re
import urllib2
import datetime
# from contextlib import closing
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
        hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Connection': 'close'}

        req = urllib2.Request(url, headers=hdr)
        res = urllib2.urlopen(req)

        return str(res.read())

# =================================================
#                Р И А - Н О В О С Т И
# =================================================
class Ria(Base):
    
    timeout = 20
    browser = Firefox()
    exprs_for_text = (
        re.compile('<h1.+</h1>'),
        re.compile('<div style="overflow.+[0-9]+</div>(.+)<div style'))
    
    expr_for_main_block = re.compile('(<strong>.+)</div><div id="facebook-userbar-article-end"', re.DOTALL)
    expr_for_parsing_main_block =  re.compile('<p>.+</p>')   
    # ненужные вставки в текст статьи    
    expr_for_brief = re.compile('(<div id="inject_.+</div>)[А-я]+')
    
    expr_for_date = re.compile('<div style="overflow.+>[0-9]{2}:[0-9]{2} ([0-9]{2}/[0-9]{2}/[0-9]{4})</div>.+<div style')
    expr_for_time = re.compile('<div style="overflow.+>([0-9]{2}:[0-9]{2}) [0-9]{2}/[0-9]{2}/[0-9]{4}</div>.+<div style')

    # нужно для загрузки ВСЕХ новостей за день
    def loading_full_page(self, url, pr_year, pr_month, pr_day):
        
        self.browser.get(url)
        expr = pr_year + pr_month + pr_day + '/[0-9]+'

        # пока не появятся новости предыдущего дня
        while not re.compile(expr).findall(self.browser.page_source):
            button = self.browser.find_element_by_class_name('list_pagination_next')
            button.click()
            # wait for the page to load
            WebDriverWait(self.browser, timeout = self.timeout).until(
                lambda x: x.find_element_by_class_name('list_pagination_next'))

        page_source = self.browser.page_source

        return page_source

    # вытаскиваем текст из статьи
    def get_text(self, url):
        print url
        text = []
        article = self.open_site('http://ria.ru' + url)
        
        for expr in self.exprs_for_text:
            text.extend(list(set(expr.findall(article))))
            
        main_block = self.expr_for_main_block.findall(article)
        text.extend(self.expr_for_parsing_main_block.findall(main_block[0]))
        
        metadata = self.get_metadata(article)
        
        parsed_article = ['\n\n'.join(text)]
        parsed_article.extend(metadata)
        
        return parsed_article

    # добавляем дату и время   (HH:MM, DD/MM/YYYY)
    def get_metadata(self, article):
        metadata = []
        
        metadata.extend(self.expr_for_time.findall(article))
        metadata.extend(self.expr_for_date.findall(article))
        
        return metadata
    
    # получаем ссылки на статьи с привязкой к дате
    def get_news(self, since, by):  # даты разделять точкой (после года не ставить)

        list_all_parsed = []
        list_daily_news = []
        list_of_days, day_out = self.make_days_list(since, by)[0], self.make_days_list(since, by)[1]

        for index in range(len(list_of_days)):
            # нужная дата
            day = list_of_days[index][2]
            month = list_of_days[index][1]
            year = list_of_days[index][0]

            # предыдущая дата
            if index == 0:
                pr_day = day_out[2]
                pr_month = day_out[1]
                pr_year = day_out[0]
            else:
                pr_day = list_of_days[index - 1][2]
                pr_month = list_of_days[index - 1][1]
                pr_year = list_of_days[index - 1][0]

            # общий сайт, где собраны все новости одного дня
            site_list_daily_news = self.loading_full_page('http://ria.ru/world/' + year + month + day, pr_year, pr_month, pr_day)

            # получаем ссылки на новости этого дня
            expr_for_list_daily_news = 'href="(/world/' + year + month + day + '/[0-9]+\.html)"'
            expr_for_list_daily_news = re.compile(expr_for_list_daily_news)

            list_daily_news.extend(list(set(expr_for_list_daily_news.findall(site_list_daily_news))))

        for url in list_daily_news:
            list_all_parsed.append(self.get_text(url))
            
        return list_all_parsed

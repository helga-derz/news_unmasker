# -*- coding: utf-8 -*-

import re
import os


def read_docs(name_dir):  # СЧИТЫВАЕМ ТЕКСТЫ НОВОСТИ
    list_docs = []
    for (path, dirs, files) in os.walk('data/' + name_dir):
        list_docs = files

    list_docs.sort()
    list_docs = list_docs[:-2]

    read_files = []

    for doc in list_docs:
        read_files.append(open('data/' + name_dir + '/' + doc, 'r').read())

    return read_files


def get_relations(name_dir):  # СЧИТЫВАЕМ ОТНОШЕНИЯ МЕЖДУ ФАЙЛАМИ

    relations = {}
    matrix = []

    for i in open('data/' + name_dir + '/relations.txt', 'r').read().split('\r\n'):
        matrix.append(i.split('\t'))

    count = 0

    for i in range(len(matrix) - 1):
        for j in range(len(matrix) - 1, count, -1):
            relations[name_dir[-1] + '_' + str(i) + '.' + name_dir[-1] + '_' + str(j)] = matrix[i][j]
        count += 1

    return relations


"""
def make_bag_of_words(text):           #СОБИРАЕМ ВСЕ СЛОВА БЕЗ ПУНКТУАЦИИ (РЕГИСТР НЕ ИМЕЕТ ЗНАЧЕНИЯ)

    expr = re.compile('[А-я]+')           #ЧЕ С НЕЙ?????????

    return expr.findall(text)
"""


def html_decode(text):
    html_codes = (("'", '&#39;'),
                  ('"', '&quot;'),
                  ('>', '&gt;'),
                  ('<', '&lt;'),
                  ('&', '&amp;'),
                  ('—', '&mdash;'),
                  ('—', '&ndash;'),
                  ('"', '&laquo;'),
                  ('"', '&raquo;'),
                  (' ', '&nbsp;'),
                  ('', '/'),
                  ('', '<br>'),
                  ('', '<p>'),
                  ('', '<a>'))

    for code in html_codes:
        text = text.replace(code[1], code[0])

    return text


def del_punctuation(text):  # ПЛЮС ВСЯКИЙ МУСОР

    marks = ['.', ',', '"', "'", ';', ':', '!', '?', '#', '«', '»', '§', '⸮', '-', '\n', '\t', '\r']

    for mark in marks:
        text = text.replace(mark, ' ')  # ПРОБЕЛ ДЛЯ МУДАКОВ

    return text


def del_tags(text):
    expr = re.compile('<[^А-я]+>')  # исправить косяк с текстом с гиперссылкой
    res = expr.findall(text)

    for tag in res:
        text = text.replace(tag, '')

    return text


def make_bag_of_words(text):
    clear_text = del_tags(text)
    clear_text = html_decode(clear_text)
    clear_text = del_punctuation(clear_text)

    words = clear_text.split(' ')

    while words.count('') != 0:
        words.remove('')

    return words


def compare(text1, text2):  # ВОЗВРАЩАЕТ ВЕКТОР

    bag1 = make_bag_of_words(text1)
    bag2 = make_bag_of_words(text2)

    count = 0
    for word in bag1:
        if word in bag2:
            count += 1

    vector = []
    vector.append(min(len(bag1), len(bag2)) / float(max(len(bag1), len(bag2))))
    vector.append(2 * count / float(len(bag1) + len(bag2)))

    return vector

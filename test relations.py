# -*- coding: utf-8 -*-

from psql_functoins import *
import making_vectors as mv

db = Psql()
cur = db.cur


def make_x_train():

    # создаём словарь со всеми текстами ручной разметки {индекс:текст}
    dict_texts = {}
    all_train_texts = db.select_text('train_corpus')
    for inst in all_train_texts:
        dict_texts[inst.index_text] = inst.text

    # создаём словарь {идекс1.индекс2: категория}
    dict_rels = {}
    all_train_relations = db.select_relations('train_relations')
    for inst in all_train_relations:
        dict_rels[inst.first_text + '.' + inst.second_text] = inst.relation

    # создаём вектор каждой пары из предыдущего словаря
    vectors = []
    y_train = []

    for pair, rel in dict_rels.items():

        text1 = dict_texts[pair.split('.')[0]]
        text2 = dict_texts[pair.split('.')[1]]

        vectors.append(mv.compare(text1, text2))
        y_train.append(rel)

    return vectors, y_train

# -*- coding: utf-8 -*-

from psql_functoins import *
import making_vectors as mv


def add_hand_text():  # adding texts to train corpus

    db = Psql()
    cur = db.cur

    for index_dir in range(20):
        list_sorted_texts, list_names = mv.read_docs('event' + str(index_dir))
        for index in range(len(list_names)):
            index_text = str(index_dir) + '-' + list_names[index].split('_')[0]
            cur.execute(
                    "INSERT INTO train_corpus (index_dir, index_text, name, text) VALUES (%s, %s, %s, %s)",
                    (index_dir, index_text, list_names[index], list_sorted_texts[index],))

    db.conn.commit()


def add_rel_in():  # adding relations for texts in one dir
    db = Psql()
    cur = db.cur

    for index_dir in range(20):
        relations = mv.get_relations('event' + str(index_dir))
        for pair, rel in relations.items():
            cur.execute(
                    "INSERT INTO train_relations (first_text, second_text, relation) VALUES (%s, %s, %s)",
                    (pair.split('.')[0], pair.split('.')[1], rel,))

    db.conn.commit()


def add_rel_out():   # adding relations for texts from different dirs
    db = Psql()
    cur = db.cur

    all_names = []
    for index_dir in range(20):
        for name in mv.read_docs('event' + str(index_dir))[1]:
            all_names.append(str(index_dir) + '-' + name.split('_')[0])

    for index, first_name in enumerate(all_names[:-1]):
        for second_name in all_names[index+1:]:
            if first_name.split('-')[0] != second_name.split('-')[0]:
                cur.execute(
                        "INSERT INTO train_relations (first_text, second_text, relation) VALUES (%s, %s, %s)",
                        (first_name, second_name, 3,))

    db.conn.commit()

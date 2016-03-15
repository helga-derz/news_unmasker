# -*- coding: utf-8 -*-

from psql_functoins import *
import making_vectors as mv
import classifier as cl
from sklearn.svm import SVC

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


def make_x_test():
    collection = {}
    ids = []
    for inst in db.select_text('texts', **{'publication_date': " BETWEEN '2015-01-05' AND '2015-01-05'"}):
        collection[inst.id] = inst.text
        ids.append(inst.id)

    vectors = []
    pairs = []

    for index, first_id in enumerate(ids[:-1]):
        for second_id in ids[index+1:]:
            pairs.append(str(first_id) + '.' + str(second_id))
            vectors.append(mv.compare(collection[first_id], collection[second_id]))

    return vectors, pairs


# комментить тут
print 'train data'
x_train, y_train = make_x_train()

print 'test data'
x_test, x_pairs = make_x_test()

model = SVC(kernel='precomputed')
kernel_train = cl.kernel_train(x_train)
model.fit(kernel_train, y_train)
kernel_train = None

kernel_test = cl.kernel_test(x_train, x_test)

y_predicted = model.predict(kernel_test)

for index in range(len(y_predicted)):
    cur.execute(
        "INSERT INTO test_relations (first_text, second_text, relation) VALUES (%s, %s, %s)",
        (int(x_pairs[index].split('.')[0]), int(x_pairs[index].split('.')[1]), y_predicted[index],))

db.conn.commit()


'''
n = 0
for i in range(len(y_predicted)):
    if y_test[i] == y_predicted[i]:
        n += 1

print n, len(y_test)
'''
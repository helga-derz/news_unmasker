CREATE TABLE parsers (name_parser text PRIMARY KEY, site text, describtion text, last_update date);

CREATE TABLE texts (id_text serial PRIMARY KEY, name_parser text references parsers(name_parser), url text, download_time time, download_date date, publication_time time, publication_date date, text text);

CREATE TABLE train_corpus (index_text text PRIMARY KEY, index_dir int, name text, text text);

CREATE TABLE train_relations (id serial PRIMARY KEY, first_text text references train_corpus(index_text), second_text text references train_corpus(index_text), relation int);

CREATE TABLE test_relations (id serial PRIMARY KEY, first_text serial references texts(id_text), second_text serial references texts(id_text), relation int);

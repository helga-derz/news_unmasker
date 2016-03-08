CREATE TABLE parsers (name_parser text PRIMARY KEY, site text, describtion text, last_update date);

CREATE TABLE texts (id_text serial PRIMARY KEY, name_parser text references parsers(name_parser), url text, download_time time, download_date date, publication_time time, publication_date date, text text);

CREATE TABLE train_corpus (id serial PRIMARY KEY, index_dir int, name text, text text);
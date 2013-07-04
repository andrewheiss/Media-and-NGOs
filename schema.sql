PRAGMA foreign_keys = ON;

CREATE TABLE articles (
  id_article integer PRIMARY KEY,
  article_title text NOT NULL,
  article_subtitle text,
  article_date timestamp NOT NULL,
  article_url text NOT NULL,
  article_type text NOT NULL,
  article_content text NOT NULL,
  article_content_no_tags text NOT NULL,
  article_content_no_punc text NOT NULL,
  article_word_count integer NOT NULL,
  article_translated integer
);
CREATE UNIQUE INDEX article_url_index ON articles (article_url);

CREATE TABLE "articles_authors" (
  "fk_article" integer NOT NULL,
  "fk_author" integer NOT NULL,
  FOREIGN KEY (fk_article) REFERENCES articles (id_article) ON DELETE CASCADE,
  FOREIGN KEY (fk_author) REFERENCES authors (id_author) ON DELETE CASCADE,
  PRIMARY KEY("fk_article", "fk_author")
);

CREATE TABLE "articles_sources" (
  "fk_article" integer NOT NULL,
  "fk_source" integer NOT NULL,
  FOREIGN KEY (fk_article) REFERENCES articles (id_article) ON DELETE CASCADE,
  FOREIGN KEY (fk_source) REFERENCES sources (id_source) ON DELETE CASCADE,
  PRIMARY KEY("fk_article", "fk_source")
);

CREATE TABLE "articles_tags" (
  "fk_article" integer NOT NULL,
  "fk_tag" integer NOT NULL,
  FOREIGN KEY (fk_article) REFERENCES articles (id_article) ON DELETE CASCADE,
  FOREIGN KEY (fk_tag) REFERENCES tags (id_tag) ON DELETE CASCADE,
  PRIMARY KEY("fk_article", "fk_tag")
);

CREATE TABLE authors (
  "id_author" integer PRIMARY KEY,
  "author_name" text NOT NULL
);
CREATE UNIQUE INDEX author_index ON authors (author_name);

CREATE TABLE sources (
  "id_source" integer PRIMARY KEY,
  "source_name" text NOT NULL
);
CREATE UNIQUE INDEX source_index ON sources (source_name);

CREATE TABLE tags (
  "id_tag" integer PRIMARY KEY,
  "tag_name" text NOT NULL
);
CREATE UNIQUE INDEX tag_index ON tags (tag_name);
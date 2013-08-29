#!/usr/bin/env python3

# SQL poop...
# SELECT A.article_title, C.author_name FROM articles AS A 
#   LEFT JOIN articles_authors AS B ON (A.id_article = B.fk_article)
#   LEFT JOIN authors as C on (B.fk_author = C.id_author)

# SELECT id_article, article_title, article_date, article_url, article_type, article_content_no_tags, article_translated FROM articles ORDER BY RANDOM() LIMIT 50

# See also http://www.lornajane.net/posts/2011/inner-vs-outer-joins-on-a-many-to-many-relationship

# Text analysis poop...
# from collections import Counter
# word_list = content_no_punc.split()
# self.word_list = Counter(word_list).most_common()

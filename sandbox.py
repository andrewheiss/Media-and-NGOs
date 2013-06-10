#!/usr/bin/env python3

# SQL poop...
# SELECT A.article_title, C.author_name FROM articles AS A 
#   LEFT JOIN articles_authors AS B ON (A.id_article = B.fk_article)
#   LEFT JOIN authors as C on (B.fk_author = C.id_author)

# Text analysis poop...
# from collections import Counter
# word_list = content_no_punc.split()
# self.word_list = Counter(word_list).most_common()

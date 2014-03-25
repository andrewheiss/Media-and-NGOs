#!/usr/bin/env python3

# Title:          manual_fixes.py
# Description:    Provides a basic interface to add articles to the database one 
#                 at a time. Useful for adding files with HTML issues that didn't 
#                 get slurped up by parse_html.py.
# Author:         Andrew Heiss
# Last updated:   2013-08-09
# Python version: ≥3.0
# Usage:          Configure which database you want to add to, then paste all the 
#                 information from an article into the variables below.

#---------------------
# Database to add to
#---------------------
database = 'Corpora/dne.db'


# Import modules
from datetime import datetime
import string
import sqlite3
import re

#----------------------------
#----------------------------
# Manually paste stuff here
#----------------------------
my_title = "Coptic voters select three out of five papal nominees"
my_subtitle = ""
# my_article_date = datetime.strptime('Tuesday 19 Mar 2013', '%A %d %b %Y')  # Ahram
my_article_date = datetime.strptime('October 29, 2012', '%B %d, %Y')  # DNE
my_authors = ['']
my_sources = ['Daily News Egypt']
my_url = 'http://www.dailynewsegypt.com/2012/10/29/coptic-voters-select-three-out-of-five-papal-nominees/'
tags = ['Daily News Egypt', 'DNE', 'egypt', 'Papa Elections']
my_article_type = 'News'
my_translated = False
my_content_no_tags = """Monday’s election will determine which three papal candidates out of the remaining five will be part of the Church’s ballot next Sunday, and potentially be selected as the 118th Pope of the Coptic Orthodox Church.
The papal selection is the first in 41 years and follows the death of Pope Shenouda III in March. The new pope will take his post at a critical point, as the Church faces a number of internal and external issues.
"""
my_content = """<p>Monday’s election will determine which three papal candidates out of the remaining five will be part of the Church’s ballot next Sunday, and potentially be selected as the 118th Pope of the Coptic Orthodox Church.</p>
<p>The papal selection is the first in 41 years and follows the death of Pope Shenouda III in March. The new pope will take his post at a critical point, as the Church faces a number of internal and external issues.</p>
"""
#----------------------------
# NO MORE PASTING! STOP!!1!
#----------------------------
#----------------------------

# Automatic stuff
punc = string.punctuation.replace('-', '') + '–—”’“‘'  # Define punctuation
regex = re.compile('[%s]' % re.escape(punc))
my_content_no_punc = regex.sub(' ', my_content_no_tags.lower())  # Remove punctuation and make everything lowercase
my_word_count = len(my_content_no_punc.split())
my_tags = [tag.strip().lower() for tag in tags]  # Clean each tag


# Simplified Article class
# If I cared more about efficiency or DRY or whatever, I could make this inherit
# Article in parse_html.py, or even import that class here. Oh well. It works :)
class SingleArticle:
  """docstring for Article"""
  def __init__(self, title, subtitle, article_date, authors, sources, content, content_no_tags, content_no_punc, word_count, url, article_type, tags, translated):
    self.title = title
    self.subtitle = subtitle
    self.date = article_date
    self.authors = authors
    self.sources = sources
    self.content = content
    self.content_no_tags = content_no_tags
    self.content_no_punc = content_no_punc
    self.word_count = word_count
    self.url = url
    self.type = article_type
    self.tags = tags
    self.translated = translated

  def report(self):
    """Print out everything (for testing purposes)"""
    print("Title:", self.title)
    print("Subtitle:", self.subtitle)
    print("Date:", self.date)
    print("Authors:", self.authors)
    print("Sources:", self.sources)
    print("Content:", self.content)
    print("Just text:", self.content_no_tags)
    print("No punctuation:", self.content_no_punc)
    print("Word count:", self.word_count)
    print("URL:", self.url)
    print("Type:", self.type)
    print("Tags:", self.tags)
    print("Translated:", self.translated)

  def write_to_db(self, conn, c):
    """Write the article object to the database

    Arguments:
      conn = sqlite3 databse connection
      c = sqlite3 database cursor on `conn`
    """
    # Insert article
    c.execute("""INSERT OR IGNORE INTO articles 
      (article_title, article_subtitle, article_date, article_url, 
        article_type, article_content, article_content_no_tags, 
        article_content_no_punc, article_word_count, article_translated) 
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
      (self.title, self.subtitle, self.date, self.url, 
        self.type, self.content, self.content_no_tags, 
        self.content_no_punc, self.word_count, self.translated))
    c.execute("""SELECT id_article FROM articles WHERE article_url = ?""", [self.url])
    article_in_db = c.fetchall()
    article_id = article_in_db[0][0]


    # Insert author(s)
    c.executemany("""INSERT OR IGNORE INTO authors (author_name) 
      VALUES (?)""", 
      [(author, ) for author in self.authors])

    # Get the ids of all the authors
    c.execute("""SELECT id_author FROM authors 
      WHERE author_name IN ({0})""".format(', '.join('?' for _ in self.authors)), self.authors)
    authors_in_db = c.fetchall()
    author_ids = [author[0] for author in authors_in_db]


    # Insert source(s)
    c.executemany("""INSERT OR IGNORE INTO sources (source_name) 
      VALUES (?)""", 
      [(source, ) for source in self.sources])

    # Get the ids of all the sources
    c.execute("""SELECT id_source FROM sources 
      WHERE source_name IN ({0})""".format(', '.join('?' for _ in self.sources)), self.sources)
    sources_in_db = c.fetchall()
    source_ids = [source[0] for source in sources_in_db]


    # Insert tag(s)
    c.executemany("""INSERT OR IGNORE INTO tags (tag_name) 
      VALUES (?)""", 
      [(tag, ) for tag in self.tags])

    # Get the ids of all the tags
    c.execute("""SELECT id_tag FROM tags 
      WHERE tag_name IN ({0})""".format(', '.join('?' for _ in self.tags)), self.tags)
    tags_in_db = c.fetchall()
    tag_ids = [tag[0] for tag in tags_in_db]


    # Insert ids into junction tables
    c.executemany("""INSERT OR IGNORE INTO articles_sources 
      (fk_article, fk_source) 
      VALUES (?, ?)""",
      ([(article_id, source) for source in source_ids]))

    c.executemany("""INSERT OR IGNORE INTO articles_authors
      (fk_article, fk_author) 
      VALUES (?, ?)""",
      ([(article_id, author) for author in author_ids]))

    c.executemany("""INSERT OR IGNORE INTO articles_tags
      (fk_article, fk_tag) 
      VALUES (?, ?)""",
      ([(article_id, tag) for tag in tag_ids]))

    # Close everything up
    conn.commit()


#----------------------------------------
# Insert the articles into the database
#----------------------------------------
# Connect to the database
# PARSE_DECLTYPES so datetime works (see http://stackoverflow.com/a/4273249/120898)
conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
c = conn.cursor()

# # Turn on foreign keys
c.execute("""PRAGMA foreign_keys = ON""")

# Write article to database
article = SingleArticle(my_title, my_subtitle, my_article_date, my_authors, my_sources, my_content, my_content_no_tags, my_content_no_punc, my_word_count, my_url, my_article_type, my_tags, my_translated)
# article.report()
article.write_to_db(conn, c)

# Close everything up
c.close()
conn.close()

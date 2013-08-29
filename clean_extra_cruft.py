#!/usr/bin/env python3

# Title:          clean_extra_cruft.py
# Description:    When initially importing the articles, I forgot to strip out <style> tags 
#                 from all three publications and Word HTML comments from Daily News Egypt 
#                 and Egypt Independent. This script finds all database entries with errant 
#                 tags and re-cleans the content.
# Author:         Andrew Heiss
# Last updated:   2013-08-28
# Python version: ≥3.0
# Usage:          Edit the database variable AND modify the SQL SELECT statement to search for the correct offending entries


# Database to work with
database = 'Corpora/egypt_independent.db'

# Import modules
import sqlite3
import string
import re
from bs4 import BeautifulSoup, Comment
from parse_html import Article  # Import functions from parse_html.py

# Connect to database
conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
conn.row_factory = sqlite3.Row  # Use a dictionary cursor
c = conn.cursor()

# Turn on foreign keys (just for fun)
c.execute("""PRAGMA foreign_keys = ON""")

# Select potentially offending articles
# c.execute("SELECT * FROM articles WHERE article_content LIKE \"%<style type%\"")
# c.execute("SELECT * FROM articles WHERE article_content LIKE \"%if gte%\"")
c.execute("SELECT * FROM articles WHERE article_content_no_tags LIKE \"%<%\"")

rows = c.fetchall()  # Get the results

# Loop through the results
for row in rows:
  id_article = row['id_article']

  # Remove lame Word HTML comments
  soup = BeautifulSoup(row['article_content'])
  for comment in soup.findAll(
    text=lambda text: isinstance(text, Comment)):
    comment.extract()
  article_content = str(soup)

  # Re-clean the content
  article_content_fixed = Article._strip_extra_tags(None, article_content)

  # Strip all tags
  fixed_list = article_content_fixed.split('\n')  # Split
  article_content_no_tags_fixed = [Article._strip_all_tags(None, chunk) for chunk in fixed_list]
  article_content_no_tags_fixed = '\n'.join([chunk for chunk in article_content_no_tags_fixed if chunk != ''])

  # No punctuation
  punc = string.punctuation.replace('-', '') + '–—”’“‘'  # Define punctuation
  regex = re.compile('[%s]' % re.escape(punc))
  article_content_no_punc_fixed = regex.sub(' ', article_content_no_tags_fixed.lower()) 

  # Word count
  word_count_fixed = len(article_content_no_punc_fixed.split())

  # Update the entry with the cleaned and fixed data
  c.execute("UPDATE articles SET article_content=?, article_content_no_tags=?, article_content_no_punc=?, article_word_count=? WHERE id_article=?", (article_content_fixed, article_content_no_tags_fixed, article_content_no_punc_fixed, word_count_fixed, id_article))
  conn.commit()


# Close everything up
c.close()
conn.close()

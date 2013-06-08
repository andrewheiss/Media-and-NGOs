#!/usr/bin/env python3

# Import modules
from bs4 import BeautifulSoup
from datetime import datetime
from subprocess import check_output, call
import string
import sqlite3
import re


#----------------------
# Classes and methods
#----------------------
class Article:
  """Parse a given HTML file with BeautifulSoup

  Attributes:
    title: Title as string
    date: Date as date object
    authors: List of author(s)
    sources: List of source(s) (mostly for articles translated from al-Masry al-Youm Arabic)
    content: HTML content as string
    content_no_tags: Tag-free version of HTML content as string
    word_list: List of all words in the articles_authors
    word_count: Lenght of `word_list`
    url: URL as string
    type: Type of article (news or opinion) as string
    tags: List of tag(s)

  Returns:
    A new article object
  """
  def __init__(self, html_file):
    self._verify_encoding(html_file)
    self._extract_fields(html_file)


  def _extract_fields(self, html_file):
    """Extract elements of the article using BeautifulSoup"""
    soup = BeautifulSoup(open(html_file,'r'))

    title_raw = soup.select('.pane-node-title div')
    title_clean = ' '.join([str(tag).strip() for tag in title_raw[0].contents])
    self.title = title_clean

    source_raw = soup.select('.field-field-source .field-items a')
    source_clean = [source.string.strip() for source in source_raw]
    self.sources = source_clean

    author_raw = soup.select('.field-field-author .field-items a')
    author_clean = [author.string.strip() for author in author_raw]
    self.authors = author_clean

    date_raw = soup.select('.field-field-published-date span')
    date_clean = date_raw[0].string.strip()
    # strptime() defines a date format for conversion into an actual date object
    date_object = datetime.strptime(date_clean, '%a, %d/%m/%Y - %H:%M')
    self.date = date_object

    tags_raw = soup.select('.view-free-tags .field-content a')
    tags = [tag.string.strip() for tag in tags_raw]
    self.tags = tags

    # Regular HTML content
    content_raw = soup.select('.pane-node-body div')
    content_clean = [str(line) for line in content_raw[0].contents if line != '\n']  # Remove list elements that are just newlines
    self.content = "\n".join(content_clean)

    # Tag-free content
    content_no_tags = ' '.join([self._strip_tags(chunk) for chunk in content_clean])
    self.content_no_tags = content_no_tags

    # Just words
    # Remove all punctuation except '-'
    regex = re.compile('[%s]' % re.escape(string.punctuation.replace('-', '')))
    word_list = regex.sub(' ', self.content_no_tags.lower())
    self.word_list = word_list.split()
    self.word_count = len(self.word_list)

    # Fortunately EI used Facebook's OpenGraph, so there's a dedicated meta tag for the URL
    # Example: <meta property="og:url" content="http://www.egyptindependent.com/opinion/beyond-sectarianism">
    url = soup.find('meta', {'property':'og:url'})['content']
    self.url = url

    self.type = "News"  # TODO: Make this more dynamic


  def report(self):
    """Print out everything (for testing purposes)"""
    print("Title:", self.title)
    print("Date:", self.date)
    print("Authors:", self.authors)
    print("Sources:", self.sources)
    print("Content:", self.content)
    print("Just text:", self.content_no_tags)
    print("Word list:", self.word_list)
    print("Word count:", self.word_count)
    print("URL:", self.url)
    print("Type:", self.type)
    print("Tags:", self.tags)


  def _verify_encoding(self, html_file):
    """If the file is improperly encoded (thanks wget!), convert it to UTF-8"""
    encoding_output = check_output(['file', '-I', html_file], universal_newlines=True)  # Check file encoding
    if 'unknown-8bit' in encoding_output:
      fp = open(html_file, 'r+')
      call(['iconv', '-f', 'ISO-8859-1', '-t', 'UTF-8', html_file], stdout=fp)  # Convert to UTF-8 with iconv
      fp.close()


  def _strip_tags(self, html):
    """Remove all HTML tags from the given string"""
    html_bs = BeautifulSoup(html)
    html_list = html_bs.find_all(text=True)  # Get only the text from all tags
    html_list = [chunk.strip() for chunk in html_list if chunk.strip() != '']  # Remove blank list elements
    return(' '.join(html_list))  # Return a string of all list elements combined


# Choose file to parse
# TODO: Loop through all the files in a folder and do this over and over...
# html_file = 'test_files/beyond-sectarianism.html'
html_file = 'test_files/100-days-morsy-report-suggests-varied-progress-president-s-goals.html'
# html_file = 'test_files/70-year-old-accused-raping-child-new-cairo.html'
art1 = Article(html_file)
art1.report()


import sys
sys.exit()

# SQL poop...


# SELECT A.article_title, C.author_name FROM articles AS A 
#   LEFT JOIN articles_authors AS B ON (A.id_article = B.fk_article)
#   LEFT JOIN authors as C on (B.fk_author = C.id_author)

conn = sqlite3.connect('egypt_independent.db')
c = conn.cursor()
# Turn on foreign keys
c.execute("""PRAGMA foreign_keys = ON""")



# Insert article
c.execute("""INSERT OR IGNORE INTO articles 
  (article_title, article_date, article_content, article_content_no_tags, article_url, article_type) 
  VALUES (?, ?, ?, ?, ?, ?)""", 
  (title_clean, date_object, "\n".join(content_clean), content_no_tags, url, article_type))
article_id = c.lastrowid
print(article_id)

authors = author_clean
sources = source_clean

# Insert author(s)
c.executemany("""INSERT OR IGNORE INTO authors (author_name) 
  VALUES (?)""", 
  [(author, ) for author in authors])

# Get the ids of all the authors
c.execute("""SELECT id_author FROM authors 
  WHERE author_name IN ({0})""".format(', '.join('?' for _ in authors)), authors)
authors_in_db = c.fetchall()
author_ids = [author[0] for author in authors_in_db]
print(author_ids)


# Insert tag(s)
c.executemany("""INSERT OR IGNORE INTO tags (tag_name) 
  VALUES (?)""", 
  [(tag, ) for tag in tags])

# Get the ids of all the tags
c.execute("""SELECT id_tag FROM tags 
  WHERE tag_name IN ({0})""".format(', '.join('?' for _ in tags)), tags)
tags_in_db = c.fetchall()
tag_ids = [tag[0] for tag in tags_in_db]
print(tag_ids)


# Insert source(s)
c.executemany("""INSERT OR IGNORE INTO sources (source_name) 
  VALUES (?)""", 
  [(source, ) for source in sources])

# Get the ids of all the sources
c.execute("""SELECT id_source FROM sources 
  WHERE source_name IN ({0})""".format(', '.join('?' for _ in sources)), sources)
sources_in_db = c.fetchall()
source_ids = [source[0] for source in sources_in_db]
print(source_ids)




# # Insert the mapping
# c.execute("""INSERT INTO articles_authors 
#   (fk_article, fk_author) 
#   VALUES (?, ?)""",
#   (article_id, author_id))

conn.commit()
# c.close()
conn.close()


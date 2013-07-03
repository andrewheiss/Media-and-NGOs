#!/usr/bin/env python3

# Title:          parse_html.py
# Description:    Loop through a directory of HTML files, parse their content with 
#                 BeautifulSoup, and insert the resultant data into an SQLite database.
# Author:         Andrew Heiss
# Last updated:   2013-07-01
# Python version: ≥3.0
# Usage:          Edit the two variables below and run the script
# Issues:         Egypt Independent: 
#                   * a few files have '(All day)' instead of a time (changed aribtrarily by hand to 8:00)
#                   * a few files didn't actually finish downloading (downloaded manually)
#                   * a couple articles have Word HTML cruft that I don't automatically 
#                     filter out. Fix them manually in the SQLite database.
#                     (Find them with: SELECT * FROM articles WHERE article_content LIKE "%if gte%")

#--------------------
# Configure parsing
#--------------------
database = 'egypt_independent.db'  # Create this beforehand; schema is in `schema.sql`
files_to_parse = 'ahram_test/*'  # Needs * to work properly


#---------------------------------------------------------------------
#---------------------------------------------------------------------
# Do the actual parsing. You shouldn't need to edit below this line.
#---------------------------------------------------------------------
#---------------------------------------------------------------------

# Import modules
from bs4 import BeautifulSoup
from datetime import datetime
from subprocess import check_output, call
from itertools import groupby
import string
import sqlite3
import re
import glob


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
    content_no_punc: Punctuation-free, lowercase version of content as string
    word_count: Length of `word_list`
    url: URL as string
    type: Type of article (news or opinion) as string
    tags: List of tag(s)
    translated: Boolean indicating whether the article is a translation

  Returns:
    A new article object
  """
  def __init__(self, html_file):
    """Create the article object

    Arguments:
      html_file: String of path to file to be parsed
    """
    # self._verify_encoding(html_file)  # Not needed for files downloaded with httrack!
    self._extract_fields_ahram(html_file)


  def _extract_fields_egind(self, html_file):
    """Extract elements of the article using BeautifulSoup"""
    soup = BeautifulSoup(open(html_file,'r'))

    # Title
    title_raw = soup.select('.pane-node-title div')
    title_clean = ' '.join([str(tag).strip() for tag in title_raw[0].contents])
    self.title = title_clean

    # Source
    source_raw = soup.select('.field-field-source .field-items a')
    source_clean = [source.string.strip() for source in source_raw]
    self.sources = source_clean

    # Author
    author_raw = soup.select('.field-field-author .field-items a')
    author_clean = [author.string.strip() for author in author_raw]
    self.authors = author_clean

    # Date
    date_raw = soup.select('.field-field-published-date span')
    date_clean = date_raw[0].string.strip()
    # strptime() defines a date format for conversion into an actual date object
    date_object = datetime.strptime(date_clean, '%a, %d/%m/%Y - %H:%M')
    self.date = date_object

    # Tags
    tags_raw = soup.select('.view-free-tags .field-content a')
    tags = [tag.string.strip().lower() for tag in tags_raw]
    self.tags = tags

    # Content
    content_raw = soup.select('.pane-node-body div')
    content_clean = [str(line) for line in content_raw[0].contents if line != '\n']  # Remove list elements that are just newlines
    self.content = "\n".join(content_clean)

    # Tag-free content
    content_no_tags = '\n'.join([self._strip_all_tags(chunk) for chunk in content_clean])
    self.content_no_tags = content_no_tags

    # Just words and word count
    punc = string.punctuation.replace('-', '') + '—”’“‘'  # Define punctuation
    regex = re.compile('[%s]' % re.escape(punc))
    content_no_punc = regex.sub(' ', self.content_no_tags.lower())  # Remove punctuation and make everything lowercase
    self.content_no_punc = content_no_punc
    self.word_count = len(content_no_punc.split())

    # URL
    # Fortunately EI used Facebook's OpenGraph, so there's a dedicated meta tag for the URL
    # Example: <meta property="og:url" content="http://www.egyptindependent.com/opinion/beyond-sectarianism">
    url = soup.find('meta', {'property':'og:url'})['content']
    self.url = url

    # Type
    # Determine the article type based on the URL (opinion or news)
    self.type = 'Opinion' if '/opinion/' in self.url else 'News'

    # Translation
    # Look at the last paragraph of the article to see if it says "translated," "translation," etc.
    self.translated = True if 'translat' in content_clean[-1] else False


  def _extract_fields_ahram(self, html_file):
    """Extract elements of the article using BeautifulSoup"""
    soup = BeautifulSoup(open(html_file,'r'))

    # Title
    title_raw = soup.select('#ContentPlaceHolder1_hd')
    title_clean = ' '.join([str(tag).strip() for tag in title_raw[0].contents])
    self.title = self._strip_all_tags(title_clean)


    # Parse date and sources
    source_and_date_blob = soup.select('#ContentPlaceHolder1_source')
    source_and_date = ' '.join([str(tag).strip() for tag in source_and_date_blob[0].contents])

    # Stupid non-semantic al-Ahram doesn't do this consistently. Some sources
    # are separated by commas, some by 'and', and some even by two spaces.
    # Some sources also have an 'and' within parentheses that technically
    # doesn't mean that there are separate sources (like 'Egyptian Elections
    # Watch (Ahram Online and Jadaliyya)'). However, it's difficult to keep
    # those all together, so instead I replace all the parentheses with spaces
    # so that Ahram Online, Jadaliyya and EEW all count as separate sources.
    source_and_date = re.sub('(\(|\))', ' ' , source_and_date)  # Replace parentheses with spaces
    source_and_date_split = re.split(',|and|  ', source_and_date)  # Split the string on commans, 'and', and double spaces


    # Date
    # The date is the last element of the list
    date_clean = source_and_date_split.pop().strip()  
    # strptime() defines a date format for conversion into an actual date object
    date_object = datetime.strptime(date_clean, '%A %d %b %Y')
    self.date = date_object


    # Sources
    # Anything that's left is a source
    source_clean = [source.strip() for source in source_and_date_split if source != '']  # Remove blank entries
    self.sources = source_clean

    self.authors = None  # Temporary...

    # TODO: Find missing articles


    # Content
    # Al-Ahram sticks all their content and tag metadata in the same messy div. 
    # This collects the whole mess into content_blob_raw, cleans it up, and then splits 
    # the list into two chunks for futher cleaning and processing.
    content_blob_raw = soup.select('#ContentPlaceHolder1_divContent')
    
    # Remove list elements that aren't newlines and remove all extra newlines and tabs
    trans_table = {'\n': None, '\t': None, '\xa0': ' '}  # Define which characters to remove
    content_blob = [str(line).translate(str.maketrans(trans_table)) for line in content_blob_raw[0].contents if line != '\n']

    # Split the list using the 'Short link: ' text (via
    # http://stackoverflow.com/a/14529615/120898) There should be two parts,
    # the content (plus tags, if they exist) and the short link input field.
    # It would be easier to use the line_inner_AfterTopic div as the divider,
    # but not all pages have that (curse you proprietary ASP CMS), so instead
    # this uses the "Short link: " text as the divider. The tag section is
    # then extracted from the content using BeautifulSoup.
    content_blob_split_iter = groupby(content_blob, lambda x: x == 'Short link: ')
    content_blob_split = [list(group) for k, group in content_blob_split_iter if not k]
    content_raw = content_blob_split[0]

    # Extract keywords from content
    content_soup = BeautifulSoup('\n'.join(content_raw))
    tags_raw = content_soup.select('.search_word')
    [tag.extract() for tag in tags_raw]

    # Clean content
    content_raw = [str(line) for line in content_soup.contents if line != '\n']  # Get raw contents
    content_clean = [self._strip_extra_tags(chunk) for chunk in content_raw]  # Clean tags
    content_clean = [chunk for chunk in content_clean if chunk != '']  # Remove empty items
    self.content = "\n".join(content_clean)
    
    # TODO: Remove Word HTML crap ([if gte mso 9]><xml> <o:DocumentProperties>  <o:Revision>0</o:Revision>, etc.)

    # Tag-free content
    content_no_tags = '\n'.join([self._strip_all_tags(chunk) for chunk in content_clean])
    self.content_no_tags = content_no_tags

    # Just words and word count
    punc = string.punctuation.replace('-', '') + '—”’“‘'  # Define punctuation
    regex = re.compile('[%s]' % re.escape(punc))
    content_no_punc = regex.sub(' ', self.content_no_tags.lower())  # Remove punctuation and make everything lowercase
    self.content_no_punc = content_no_punc
    self.word_count = len(content_no_punc.split())


    # TODO: Type
    # TODO: Translation
    # TODO: Subtitle


    # Tags
    tags_string = self._strip_all_tags(str(tags_raw[0]))  # Strip all HTML
    tags_clean = tags_string.replace('Search Keywords: ', '')  # Remove non-tag text
    tags_split = tags_clean.split('|')  # Split along pipe characters
    tags = [tag.strip().lower() for tag in tags_split]  # Clean each tag
    self.tags = tags


    # URL
    # shortlink = soup.find('input', {'class':'text_inner_ShortLink'})['value']  # Beautiful Soup way...
    url_raw = ''.join(content_blob_split[1])  # Make raw HTML a single string
    shortlink = re.search("value=\"(\\d+).html\"", url_raw).group(1)  # Find the number of the shortlink
    url = 'http://english.ahram.org.eg/News/{0}.aspx'.format(shortlink)  # Insert shortlink into URL
    self.url = url
    

    # Type
    # Determine the article type based on the URL (opinion or news)
    # self.type = 'Opinion' if '/opinion/' in self.url else 'News'

    # Translation
    # No explicit translations in al-Ahram
    self.translated = False


  def report(self):
    """Print out everything (for testing purposes)"""
    print("Title:", self.title)
    # print("Date:", self.date)
    # print("Authors:", self.authors)
    print("Sources:", self.sources)
    # print("Content:", self.content)
    # print("Just text:", self.content_no_tags)
    # print("No punctuation:", self.content_no_punc)
    print("Word count:", self.word_count)
    # print("URL:", self.url)
    # print("Type:", self.type)
    # print("Tags:", self.tags)
    # print("Translated:", self.translated)


  def write_to_db(self, conn, c):
    """Write the article object to the database

    Arguments:
      conn = sqlite3 databse connection
      c = sqlite3 database cursor on `conn`
    """
    # Insert article
    c.execute("""INSERT OR IGNORE INTO articles 
      (article_title, article_date, article_url, article_type, 
        article_content, article_content_no_tags, 
        article_content_no_punc, article_word_count, article_translated) 
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
      (self.title, self.date, self.url, self.type, 
        self.content, self.content_no_tags, 
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


  def _verify_encoding(self, html_file):
    """If the file is improperly encoded (thanks wget!), convert it to UTF-8"""
    encoding_output = check_output(['file', '-I', html_file], universal_newlines=True)  # Check file encoding
    if 'unknown-8bit' in encoding_output:
      fp = open(html_file, 'r+')
      call(['iconv', '-f', 'ISO-8859-1', '-t', 'UTF-8', html_file], stdout=fp)  # Convert to UTF-8 with iconv
      fp.close()


  def _strip_all_tags(self, html):
    """Remove all HTML tags from the given string"""
    html_bs = BeautifulSoup(html)
    html_list = html_bs.find_all(text=True)  # Get only the text from all tags
    html_list = [chunk.strip() for chunk in html_list if chunk.strip() != '']  # Remove blank list elements
    return(' '.join(html_list))  # Return a string of all list elements combined

  def _strip_extra_tags(self, html):
    """Remove <script>, <br>, and <div> tags from the given string"""
    html_bs = BeautifulSoup(html)
    to_extract = html_bs.find_all(['script', 'br', 'div'])  # Choose tags to extract
    [item.extract() for item in to_extract]  # Get rid of extraneous tags
    return(str(html_bs))  # Return string of original HTML


#----------------------------------------
# Insert the articles into the database
#----------------------------------------
# Connect to the database
# PARSE_DECLTYPES so datetime works (see http://stackoverflow.com/a/4273249/120898)
# conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
# c = conn.cursor()

# Turn on foreign keys
# c.execute("""PRAGMA foreign_keys = ON""")

# Loop through the list, parse each file, and write it to the database
# for html_file in [html_file for html_file in glob.glob(files_to_parse)]:
#   print('\n'+html_file)
#   article = Article(html_file)
#   article.report()
  # article.write_to_db(conn, c)

# CLose everything up
# c.close()
# conn.close()


# html_file = 'ahram_test/17145.html'  # Multiple authors
# html_file = 'ahram_test/24919.html'  # Word HTML junk
html_file = 'ahram_test/24939.html'  # With Jadaliyya
# html_file = 'ahram_test/310.html'  # Source, source, date
# html_file = 'ahram_test/317.html'  # No source
# html_file = 'ahram_test/438.html'  # Source  source

print('\n'+html_file)
article = Article(html_file)
article.report()

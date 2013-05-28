#!/usr/bin/env python3

# Import modules
from bs4 import BeautifulSoup
from datetime import datetime
from subprocess import check_output, call

# Choose file to parse
# TODO: Loop through all the files in a folder and do this over and over...
html_file = 'test/zamalek-salad-bars-low-calorie-options-sweltering-ramadan-summers'


#-------------------------
# Check and fix encoding
#-------------------------
# If the file is improperly encoded (thanks wget!), convert it to UTF-8
# call(['file', '-I', html_file], universal_newlines=True)  # Check file encoding
encoding_output = check_output(['file', '-I', html_file], universal_newlines=True)
if 'unknown-8bit' in encoding_output:
  fp = open(html_file, 'r+')
  call(['iconv', '-f', 'ISO-8859-1', '-t', 'UTF-8', html_file], stdout=fp)
  fp.close()


#-----------------------------------------
# Parse the HTML file with BeautifulSoup
#-----------------------------------------
soup = BeautifulSoup(open(html_file,'r'))

def clean_tag(tag):  # Use with map()
  return(str(tag).strip())  # Convert to string and strip whitespace

title_raw = soup.select('.pane-node-title div')
title_clean = ' '.join(map(clean_tag, title_raw[0].contents))  # map() is kind of like lapply() in R...
print("Title:", title_clean)


source_raw = soup.select('.field-field-source .field-items a')
source_clean = [source.string.strip() for source in source_raw]
print("Source:", source_clean)

author_raw = soup.select('.field-field-author .field-items a')
author_clean = [author.string.strip() for author in author_raw]
print("Author:", author_clean)


date_raw = soup.select('.field-field-published-date span')
date_clean = date_raw[0].string.strip()
# strptime() defines a date format for conversion into an actual date object
date_object = datetime.strptime(date_clean, '%a, %d/%m/%Y - %H:%M')
print("Date:", date_object)


tags_raw = soup.select('.view-free-tags .field-content a')
tags = [tag.string.strip() for tag in tags_raw]
print("Tags:", tags)


content_raw = soup.select('.pane-node-body div')
content_clean = [str(line) for line in content_raw[0].contents if line != '\n']  # Remove list elements that are just newlines
print("Content:", content_clean)

# TODO: URL
# TODO: Tagless version of content
# TODO: Make this all a class
# TODO: Figure out best way to store all this. XML? sqlite?

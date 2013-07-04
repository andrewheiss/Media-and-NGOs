#!/usr/bin/env python3

# Title:          finish_ahram.py
# Description:    Despite running for days and days, httrack wasn't able to get everything from 
#                 al-Ahram. However, al-Ahram has a cool system of sequential shortlinks for its 
#                 articles (though not all numbers are used). This script compares the list of 
#                 shortlinks for the articles that actually downloaded with a list of potential 
#                 article shortlinks. It then generates a list of wget commands in a bash script 
#                 that can then be run to download everything. al-Ahram doesn't believe in actual 
#                 404 pages and instead delivers its own, so wget ends up downloading every shortlink 
#                 regardless of whether or not it actually exists. Blergh. 
#                 Also, I could probably do this more efficiently inside Python with urllib2 instead 
#                 of wget, but I don't want to spend the time figuring that out. So we get this 
#                 solution instead :)
# Author:         Andrew Heiss
# Last updated:   2013-07-03
# Python version: ≥3.0
# Usage:          * Edit the file names below and run. 
#                 * Run the resultant bash script (either locally or on a server somewhere)
#                 * Filter the downloaded files in bash with `grep -l "Page doesn.t exist" *.html | xargs rm`

#---------
# Set up
#---------
ahram_news = "/Users/andrew/Downloads/ahram/blah/english.ahram.org.eg/News/*"  # Needs trailing /*
pickle_file = 'missing.p'
wget_file = 'dowload_ahram.sh'


# Import modules
import re
import pickle
import os.path
from glob import glob

# Helper functions
def only_numbers(text):
  """Strip all non-numeric characters from a string and return the numbers"""
  text = re.sub(r'[^\d]+', '', text)
  return(int(text))

def wgetize(shortlink):
  """Build a wget command"""
  command = 'wget --adjust-extension http://english.ahram.org.eg/News/{0}.aspx'.format(shortlink)
  return(command)


if not os.path.exists(pickle_file):
  # Compare list of articles downloaded with httrack to a list of potential
  # articles. Save the numbers httrack missed (or al-Ahram didn't use) to a
  # pickle.
  existing_articles = sorted([only_numbers(article) for article in glob(ahram_news)])
  hypothetical_articles = list(range(1, 74568))
  missing_articles = [article for article in hypothetical_articles if article not in existing_articles]

  pickle.dump(missing_articles, open(pickle_file, 'wb'))
else:
  # Load pickle and create a bash script
  missing_articles = pickle.load(open(pickle_file, 'rb'))
  wget_handle = open(wget_file, 'w')
  for article in missing_articles:
    print(wgetize(article), file=wget_handle)


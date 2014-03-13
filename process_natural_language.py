#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import re
import string
import nltk
from nltk.collocations import *
import glob
import codecs
import os
from itertools import chain


#------------
# Variables
#------------
# Mallet input files
path_to_documents = "R/mallet_input/*"

# Output folder
output_folder = "R/mallet_stemmed"

# Load MALLET stopwords
stopwords = set([word.strip() for word in open("R/stopwords.txt", "r")])  # Using set() speeds up "not in" searches

# Select the stemming algorithm
stemmer = nltk.stem.snowball.EnglishStemmer()  # Newest, made by Porter in 2001(?)
# stemmer = nltk.stem.porter.PorterStemmer()  # From 1980
# stemmer = nltk.stem.lancaster.LancasterStemmer()  # From 1990

# Minimum n-gram frequency
bigram_min = 10
trigram_min = 10


#-------------------
# Helper functions
#-------------------
# Strip punctuation
def remove_punc(text):
  punc = string.punctuation.replace('-', '') + u'–—”’“‘ '  # Define punctuation
  regex = re.compile('[%s]' % re.escape(punc))
  content_no_punc = regex.sub(' ', text.lower())  # Remove punctuation and make
  return(content_no_punc)

# Loop through all the words in the document, find adjacent unigrams that
# match significat bigrams, and replace them with an underscore-separated
# token. For example, given these bigrams: 
#   bigrams = [('apple', 'orange'), ('happy', 'day'), ('big', 'house')]
# it will transform this list of words:
#   words = ['apple', 'orange', 'boat', 'car', 'happy', 'day', 'cow']
# into this:
#   words_fixed = list(replace_bigrams(words, bigrams))
#               = ['apple_orange', 'boat', 'car', 'happy_day', 'cow']
def replace_bigrams(words, bigrams):
  it = iter(words)
  dict_bigrams = dict(bigrams)
  for x in it:
    if x in dict_bigrams:
      y = it.next()
      if dict_bigrams[x] == y:
        yield '_'.join((x,y))
      else:
        yield x
        yield y
    else:
      yield x


#---------------
# Process text
#---------------
# Load documents
documents = glob.glob(path_to_documents)

# Initialize corpus-wide vocabulary
vocabulary = {}

for text_file in documents:
  # Must use codecs.open() because Unicode in Python 2.x sucks. 
  document = codecs.open(text_file, 'r', 'utf-8').read()

  # Remove punctuation, clean up whitespace, and convert to a list
  words = remove_punc(document).strip().split()

  # Remove stopwords
  no_stopwords = [word for word in words if word not in stopwords]

  # Stem remaining words
  stemmed = [stemmer.stem(word) for word in no_stopwords]

  # Add tokens to corpus vocabulary (with file name as key)
  vocabulary[os.path.basename(text_file)] = stemmed

# Create new flat corpus vocabulary
token_list = list(chain.from_iterable(vocabulary.values()))


#------------------------------------------
# Find most important bigram collocations
#------------------------------------------
# See https://nltk.googlecode.com/svn/trunk/doc/howto/collocations.html

# Bigrams
bigram_measures = nltk.collocations.BigramAssocMeasures()
bigram_finder = BigramCollocationFinder.from_words(token_list)
bigram_finder.apply_freq_filter(bigram_min)

# Get top bigrams
# Tecnically .nbest() is easier, but it doesn't return the actual association score
# ngram_limit = int(len(token_list) * 0.1)
# bigrams_pmi = bigram_finder.nbest(bigram_measures.pmi, ngram_limit)

# So use .score_ngrams() and subset the list manually
bigrams_likerat = bigram_finder.score_ngrams(bigram_measures.likelihood_ratio)

# Select only super significant bigrams
# Instead of making people install scipy, it's probably easiest to just use R for the stats stuff
# scipy.stats.chi2.ppf(0.999, 1) = qchisq(0.999, df=1) = 10.82757
critical_value = 10.82757
bigrams_significant = [bigram for bigram in bigrams_likerat if bigram[1] > critical_value]

# TODO: Save bigrams and ratios to a CSV
# Make a table like p. 163 in Manning and Schutze for top x bigrams?
# Plot likelihood ratio for bigrams, just for fun?

# Trigrams
# Necessary? Tricky because stuff like "human right" is a significant bigram,
# but also present in lots of trigrams: "violat human right", "human right
# group", "human right lawyer", etc.
# trigram_measures = nltk.collocations.TrigramAssocMeasures()
# trigram_finder = TrigramCollocationFinder.from_words(token_list)
# trigram_finder.apply_freq_filter(trigram_min)

# trigrams_likerat = trigram_finder.score_ngrams(trigram_measures.likelihood_ratio)
# print(trigrams_likerat[:10])


#--------------------------------
# Create clean, final documents
#--------------------------------
# Extract just the bigram tuples from the ngram score nested list
bigrams = set([pair[0] for pair in bigrams_significant])

# Loop through all documents in the vocabulary, join/replace bigrams, and save to disk
for document in vocabulary:
  words = vocabulary[document]
  words_fixed = replace_bigrams(words, bigrams)

  filename = output_folder + '/' + document
  with open(filename, 'w') as f:
    f.write(" ".join(words_fixed).encode('utf8'))  # Die, Unicode in Python 2.x, DIE!

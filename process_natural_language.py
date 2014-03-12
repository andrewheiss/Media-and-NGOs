#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import re
import string
import nltk
from nltk.collocations import *
import math
import glob
import codecs
from collections import defaultdict


#------------
# Variables
#------------
# Mallet input files
path_to_documents = "R/mallet_input/*"

# Load MALLET stopwords
stopwords = set([word.strip() for word in open("R/stopwords.txt", "r")])  # Using set() speeds up "not in" searches

# Select the stemming algorithm
stemmer = nltk.stem.snowball.EnglishStemmer()  # Newest, made by Porter in 2001(?)
# stemmer = nltk.stem.porter.PorterStemmer()  # From 1980
# stemmer = nltk.stem.lancaster.LancasterStemmer()  # From 1990

# Minimum n-gram frequency
bigram_min = 10


#-------------------
# Helper functions
#-------------------
# Strip punctuation
def remove_punc(text):
  punc = string.punctuation.replace('-', '') + u'–—”’“‘ '  # Define punctuation
  regex = re.compile('[%s]' % re.escape(punc))
  content_no_punc = regex.sub(' ', text.lower())  # Remove punctuation and make
  return(content_no_punc)


#---------------
# Process text
#---------------
# "NLTK taggers are designed to work with lists of sentences, where each sentence is a list of words" (http://www.nltk.org/book/ch05.html)
# But feeding the word_tokenize() function a list of sentences breaks it, and feeding it sentencified text (joining the list of sentences with .s) captures n-grams across sentence boundaries.
# So this enforces sentence boundaries manually and only calculates n-grams within sentences. 

# Tokens for each document are saved to document_tokens[]. document_tokens is then 
#   (1) appended to the corpus vocabulary list, and 
#   (2) used to generate the document's tf

# Load documents
documents = glob.glob(path_to_documents)

# Initialize corpus-wide variables
vocabulary = []
token_list = []

for text_file in documents:
# For the tf-idf version, since the document dictionary needs an integer index
# for text_file, i in zip(documents, range(len(documents))): 
  # Must use codecs.open() because Unicode in Python 2.x sucks. 
  document = codecs.open(text_file, 'r', 'utf-8').read()

  # Divide text into sentences, bounded by ? and . and \n
  sentences = [remove_punc(sentence).strip() for sentence in re.split('\.|\?|\\n', document) if sentence != '']

  # Initialize token list
  document_tokens = []

  # Remove stopwords, stem, and then tokenize and n-gramize each sentence individually. 
  for sentence in sentences:
    words = sentence.split()

    # Remove stopwords
    no_stopwords = [word for word in words if word not in stopwords]
    # no_stopwords = words

    # Stem the remaining words
    stemmed = [stemmer.stem(word) for word in no_stopwords]

    # Add tokens to list
    document_tokens.extend(stemmed)

  # Add tokens to corpus vocabulary
  # vocabulary.append(document_tokens)  # For tf-idf version, vocabulary list needs to be a nested list [[x,x], [x,x]]
  token_list.extend(document_tokens)  # For frequency version, vocabulary list just needs to be a list [x, x, x]


#------------------------------------------
# Find most important bigram collocations
#------------------------------------------
# See https://nltk.googlecode.com/svn/trunk/doc/howto/collocations.html

ngram_limit = int(len(token_list) * 0.1)

# Bigrams
bigram_measures = nltk.collocations.BigramAssocMeasures()
bigram_finder = BigramCollocationFinder.from_words(token_list)
bigram_finder.apply_freq_filter(bigram_min)

# Get top bigrams
# Tecnically .nbest() is easier, but it doesn't return the actual association score
# bigrams_pmi = bigram_finder.nbest(bigram_measures.pmi, ngram_limit)

# So use .score_ngrams() and subset the list manually
bigrams_likerat = bigram_finder.score_ngrams(bigram_measures.likelihood_ratio)

# Select only super significant bigrams
# Instead of making people install scipy, it's probably easiest to just use R for the stats stuff
# scipy.stats.chi2.ppf(0.999, 1) = qchisq(0.999, df=1) = 10.82757
crit_value = 10.82757
bigrams_sig = [bigram for bigram in bigrams_likerat if bigram[1] > crit_value]

print(bigrams_sig)

# Make a table like p. 163 in Manning and Schutze for top x bigrams?
# Plot likelihood ratio for bigrams, just for fun?



# Trigrams
# Necessary? Tricky because stuff like "human right" is a significant bigram,
# but also present in lots of trigrams: "violat human right", "human right
# group", "human right lawyer", etc.
# trigram_measures = nltk.collocations.TrigramAssocMeasures()
# trigram_finder = TrigramCollocationFinder.from_words(token_list)
# trigram_finder.apply_freq_filter(trigram_min)

# trigrams_pmi = trigram_finder.nbest(trigram_measures.pmi, ngram_limit)
# print(trigrams_pmi)



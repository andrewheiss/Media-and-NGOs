#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import re
import string
import nltk
import math
import glob
import codecs
from collections import defaultdict


# Mallet input files
path_to_documents = "mallet_test/*"

# Load MALLET stopwords
stopwords = set([word.strip() for word in open("R/stopwords.txt", "r")])  # Using set() speeds up "not in" searches

# Select the stemming algorithm
stemmer = nltk.stem.snowball.EnglishStemmer()  # Newest, made by Porter in 2001(?)
# stemmer = nltk.stem.porter.PorterStemmer()  # From 1980
# stemmer = nltk.stem.lancaster.LancasterStemmer()  # From 1990


#-------------------
# Helper functions
#-------------------
# Strip punctuation
def remove_punc(text):
  punc = string.punctuation.replace('-', '') + u'–—”’“‘ '  # Define punctuation
  regex = re.compile('[%s]' % re.escape(punc))
  content_no_punc = regex.sub(' ', text.lower())  # Remove punctuation and make
  return(content_no_punc)


# tf-idf stuff
def freq(word, doc):
  return(doc.count(word))

def word_count(doc):
  return(len(doc))

def tf(word, doc):
  return((freq(word, doc) / float(word_count(doc))))
 
def num_docs_containing(word, list_of_docs):
  count = 0
  for document in list_of_docs:
    if freq(word, document) > 0:
      count += 1
  return(1 + count)

def idf(word, list_of_docs):
  return(math.log(len(list_of_docs) / float(num_docs_containing(word, list_of_docs))))
 
def tf_idf(word, doc, list_of_docs):
  return((tf(word, doc) * idf(word, list_of_docs)))


documents = glob.glob(path_to_documents)

#---------------
# Process text
#---------------
# "NLTK taggers are designed to work with lists of sentences, where each sentence is a list of words" (http://www.nltk.org/book/ch05.html)
# But feeding the word_tokenize() function a list of sentences breaks it, and feeding it sentencified text (joining the list of sentences with .s) captures n-grams across sentence boundaries.
# So this enforces sentence boundaries manually and only calculates n-grams within sentences. 

# Tokens for each document are saved to document_tokens[]. document_tokens is then 
#   (1) appended to the corpus vocabulary list, and 
#   (2) used to generate the document's tf

# Initialize corpus-wide variables
vocabulary = []
token_list = []
docs = {}
num_unigrams = 0

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

    # Tokenize and make n-grams of stemmed words
    unigrams = stemmed

    stemmed_tokens = nltk.word_tokenize(" ".join(stemmed))  # word_tokenize requires a string, not a list
    bigrams = nltk.bigrams(stemmed_tokens)  # or nltk.ngrams(stemmed_tokens, 2)
    trigrams = nltk.trigrams(stemmed_tokens)  # or nltk.ngrams(stemmed_tokens, 3)
    quadgrams = nltk.ngrams(stemmed_tokens, 4)

    # Add tokens to list
    num_unigrams += len(unigrams)
    document_tokens.extend(unigrams)
    document_tokens.extend(bigrams)
    # document_tokens.extend(trigrams)
    # document_tokens.extend(quadgrams)

  # Add tokens to corpus vocabulary
  # vocabulary.append(document_tokens)  # For tf-idf version, vocabulary list needs to be a nested list [[x,x], [x,x]]
  token_list.extend(document_tokens)  # For frequency version, vocabulary list just needs to be a list [x, x, x]

  #-----------
  # tf stuff
  #-----------
  # # Create a new tf dictionary 'row'
  # docs[i] = {'freq': {}, 'tf': {}, 'idf': {},
  #          'tf-idf': {}, 'tokens': []}

  # # Calculate the tf for all tokens
  # for token in document_tokens:
  #   # Frequency of each token
  #   docs[i]['freq'][token] = freq(token, document_tokens)

  #   # Normalized tf (term frequency) for each token
  #   docs[i]['tf'][token] = tf(token, document_tokens)
  #   docs[i]['tokens'] = document_tokens

#---------------
# tf-idf stuff
#---------------
# Use tf-idf to determine if n-gram is important: https://gist.github.com/marcelcaraciolo/1604487 - http://aimotion.blogspot.com/2011/12/machine-learning-with-python-meeting-tf.html

# # Loop through each document and figure out the tf-idf
# for doc in docs:
#   for token in docs[doc]['tf']:
#     # Inverse document frequency (idf)
#     docs[doc]['idf'][token] = idf(token, vocabulary)

#     # tf-idf for tokens
#     docs[doc]['tf-idf'][token] = tf_idf(token, docs[doc]['tokens'], vocabulary)


# words = {}  # Keep track of words
# for doc in docs:
# #   # Look at each token in the corpus tf-idf...
#   for token in docs[doc]['tf-idf']:
#     # Store the highest tf-idf value for each word
#     if token not in words:
#       words[token] = docs[doc]['tf-idf'][token]
#     else:
#       if docs[doc]['tf-idf'][token] > words[token]:
#         words[token] = docs[doc]['tf-idf'][token]


# # Print word list, sorted by tf-idf value
# for item in sorted(words.items(), key=lambda x: x[1], reverse=True):
#   print "{0:.10f} <= {1}".format(item[1], item[0])


#------------------------
# Token frequency stuff
#------------------------
# David Banks: "one gets the frequencies of the tokens in the total corpus, and then looks for digrams, trigrams, etc. that co-occur more often than the product of their frequencies"
# Create dictionary of token frequencies

tokens = defaultdict(int)
for token in token_list:
  tokens[token] += 1


for item in sorted(tokens.items(), key=lambda x: x[1], reverse=True):
  print "{0} ({1}) {2}".format(item[1], item[1]/float(num_unigrams), item[0])

# Join significant n-grams with underscore
# Make sure MALLET doesn't throw away underscored words: add `--token-regex "\\w+"` to import-dir command


# # n-gram distributions
# fdist = nltk.FreqDist(token_list)
# # thing = fdist.plot(cumulative=True)
# for k, v in fdist.items():
#   print k, v, "{0:.10f}".format(fdist.freq(k))

# Better NLTK way: look for statisticaly significant collocations
# http://stackoverflow.com/questions/2452982/how-to-extract-common-significant-phrases-from-a-series-of-text-entries
# https://nltk.googlecode.com/svn/trunk/doc/howto/collocations.html

#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import re
import string
import nltk

sample_text = u"""Abortion in Egypt: Whose choice?

There are few options for women in Egypt who choose to undergo an abortion. Financial constraints, social stigmas, the issue of morality and “unavailable” over-the-counter medication have forced a vast number of women into backstreet abortions. Daily News Egypt explores how social, cultural and religious ideals restrict a woman’s right to choose what is best for her.

Although legal, religious and social regulations bar women in Egypt from terminating their unwanted pregnancies, many women seek to undergo abortion across the country. Whether conducted for medical or other reasons, abortion remains a controversial and hotly-debated subject in Egyptian society. In gynaecology , specialists are split between an array of perspectives. Some believe abortion is a form of murder, others think it lies within the basic rights of women to have full control over their bodies. The question of whether or not abortion is morally wrong persists in the hearts and minds of many women when thinking about terminating a pregnancy.
Scientifically, abortion is conducted through medical or surgical procedures. Medical abortion, when the foetus is completely dislodged from the uterus, is carried out using certain drugs. Dr. Hussein Gohar, Head of Gohar Women’s Health Clinic, explains there are two drugs used in abortion: Mifepristone and Misoprostol, or what is known in pharmacies as Misotac. The latter medication should be taken 48 hours after the first. “When taken together within this time frame, the success rate of abortion exceeds 90%,” he says. Mifepristone inhibits the hormone progesterone, which is responsible for maintaining pregnancy, whereas Misoprostol triggers strong uterine contractions that dislodge the foetus from the uterine walls.  Some women find it easier to end their pregnancies by using the medical procedure as a first step to secret abortion. Mifepristone is not available in Egypt. Therefore, women can only take Misotac."""


#---------------
# Set up stuff
#---------------
# Helper function to strip punctuation
def remove_punc(text):
  punc = string.punctuation.replace('-', '') + u'–—”’“‘ '  # Define punctuation
  regex = re.compile('[%s]' % re.escape(punc))
  content_no_punc = regex.sub(' ', text.lower())  # Remove punctuation and make
  return(content_no_punc)

# Divide text into sentences, bounded by ? and . and \n
sentences = [remove_punc(sentence).strip() for sentence in re.split('\.|\?|\\n', sample_text) if sentence != '']

# Load MALLET stopwords
stopwords = set([word.strip() for word in open("R/stopwords.txt", "r")])  # Using set() speeds up "not in" searches

# Select the stemming algorithm
stemmer = nltk.stem.snowball.EnglishStemmer()  # Newest, made by Porter in 2001(?)
# stemmer = nltk.stem.porter.PorterStemmer()  # From 1980
# stemmer = nltk.stem.lancaster.LancasterStemmer()  # From 1990


#---------------
# Process text
#---------------
# "NLTK taggers are designed to work with lists of sentences, where each sentence is a list of words" (http://www.nltk.org/book/ch05.html)
# But feeding the word_tokenize() function a list of sentences breaks it, and feeding it sentencified text (joining the list of sentences with .s) captures n-grams across sentence boundaries.
# So this enforces sentence boundaries manually and only calculate n-grams within sentences. 

# Remove stopwords, stem, and then tokenize and n-gramize each sentence individually. 
# Output is saved to final_tokens[]
vocabulary = []
final_tokens = []
for sentence in sentences:
  words = sentence.split()

  # Remove stopwords
  no_stopwords = [word for word in words if word not in stopwords]

  # Stem the remaining words
  stemmed = [stemmer.stem(word) for word in no_stopwords]

  # Tokenize and make n-grams of stemmed words
  unigrams = stemmed

  stemmed_tokens = nltk.word_tokenize(" ".join(stemmed))  # word_tokenize requires a string, not a list
  bigrams = nltk.bigrams(stemmed_tokens)  # or nltk.ngrams(stemmed_tokens, 2)
  trigrams = nltk.trigrams(stemmed_tokens)  # or nltk.ngrams(stemmed_tokens, 3)
  quadgrams = nltk.ngrams(stemmed_tokens, 4)

  # Add to list
  final_tokens.extend(unigrams)
  final_tokens.extend(bigrams)
  final_tokens.extend(trigrams)
  final_tokens.extend(quadgrams)

  vocabulary.append(final_tokens)


# n-gram distributions
# fdist = nltk.FreqDist(final_tokens)
# for k, v in fdist.items():
#   print k, v

# Use tf-idf to determine if n-gram is important: https://gist.github.com/AloneRoad/1605037, http://yasserebrahim.wordpress.com/2012/10/25/tf-idf-with-pythons-nltk/


# Join significant n-grams with underscore
# Make sure MALLET doesn't throw away underscored words: add `--token-regex "\\w+"` to import-dir command

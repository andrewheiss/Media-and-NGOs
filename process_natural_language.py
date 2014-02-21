#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import re
import string
import nltk

sample_text = u"""Abortion in Egypt: Whose choice?

There are few options for women in Egypt who choose to undergo an abortion. Financial constraints, social stigmas, the issue of morality and “unavailable” over-the-counter medication have forced a vast number of women into backstreet abortions. Daily News Egypt explores how social, cultural and religious ideals restrict a woman’s right to choose what is best for her.

Although legal, religious and social regulations bar women in Egypt from terminating their unwanted pregnancies, many women seek to undergo abortion across the country. Whether conducted for medical or other reasons, abortion remains a controversial and hotly-debated subject in Egyptian society. In gynaecology , specialists are split between an array of perspectives. Some believe abortion is a form of murder, others think it lies within the basic rights of women to have full control over their bodies. The question of whether or not abortion is morally wrong persists in the hearts and minds of many women when thinking about terminating a pregnancy.
Scientifically, abortion is conducted through medical or surgical procedures. Medical abortion, when the foetus is completely dislodged from the uterus, is carried out using certain drugs. Dr. Hussein Gohar, Head of Gohar Women’s Health Clinic, explains there are two drugs used in abortion: Mifepristone and Misoprostol, or what is known in pharmacies as Misotac. The latter medication should be taken 48 hours after the first. “When taken together within this time frame, the success rate of abortion exceeds 90%,” he says. Mifepristone inhibits the hormone progesterone, which is responsible for maintaining pregnancy, whereas Misoprostol triggers strong uterine contractions that dislodge the foetus from the uterine walls.  Some women find it easier to end their pregnancies by using the medical procedure as a first step to secret abortion. Mifepristone is not available in Egypt. Therefore, women can only take Misotac."""


#------------
# Sentences
#------------
# Helper function to strip punctuation
def remove_punc(text):
  punc = string.punctuation.replace('-', '') + u'–—”’“‘ '  # Define punctuation
  regex = re.compile('[%s]' % re.escape(punc))
  content_no_punc = regex.sub(' ', text.lower())  # Remove punctuation and make
  return(content_no_punc)

# Divide text into sentences, bounded by ? and . and \n
sentences = [remove_punc(sentence).strip() for sentence in re.split('\.|\?|\\n', sample_text) if sentence != '']


#-------------------
# Remove stopwords
#-------------------
# TODO: Stopwords?
# See http://stackoverflow.com/questions/19130512/stopword-removal-with-nltk
# But use the MALLET list, saving it to a set?


#-----------
# Stemming
#-----------
# Stem words in the sentences
snowball = nltk.stem.snowball.EnglishStemmer()
# porter = nltk.stem.porter.PorterStemmer()
# lancaster = nltk.stem.lancaster.LancasterStemmer()

stemmed_sentences = []
for sentence in sentences:
  stemmed = [snowball.stem(word) for word in sentence.split()]
  stemmed_sentences.append(" ".join(stemmed))


#----------
# n-grams
#----------
# "NLTK taggers are designed to work with lists of sentences, where each sentence is a list of words" (http://www.nltk.org/book/ch05.html)
# But feeding the word_tokenize() function a list of sentences breaks it, and feeding it sentencified text (joining the list of sentences with .s) captures n-grams across sentence boundaries.
# So this enforces sentence boundaries manually and only calculate n-grams within sentences. 

# Tokenize and n-gramize each sentence individually, saving to all_grams[], which gets flattened in the end
all_grams = []
for sentence in stemmed_sentences:
  stemmed_tokens = nltk.word_tokenize(sentence)
  grams = nltk.bigrams(stemmed_tokens)  # or nltk.ngrams(stemmed_tokens, 2)
  all_grams.append(grams)

grams = [item for sublist in all_grams for item in sublist]  # Flatten list

# n-gram distributions
fdist = nltk.FreqDist(grams)
for k, v in fdist.items():
  print k, v

# Use tf-idf to determine if n-gram is important: https://gist.github.com/AloneRoad/1605037, http://yasserebrahim.wordpress.com/2012/10/25/tf-idf-with-pythons-nltk/


# Join significant n-grams with underscore
# Make sure MALLET doesn't throw away underscored words

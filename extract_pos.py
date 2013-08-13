#!/usr/bin/env python3

# Title:          extract_pos.py
# Description:    Create lists of verbs and adjectives (parts of speech) used in all 
#                 articles that mention any of the signatory NGOs.
# Author:         Andrew Heiss
# Last updated:   2013-08-13
# Python version: ≥3.0
# Usage:          Edit the two variables below and run the script. You'll need to run 
#                 the script for each publication.

#-------------------
# Configure script
#-------------------
database = 'Corpora/egypt_independent.db'
publication_prefix = 'egind_'


#----------------------------------------------------------
# Import modules
from text.blob import TextBlob  # See https://textblob.readthedocs.org/en/latest/
import sqlite3
import csv
import re
from collections import Counter


# List of signatory organizations in http://www.eipr.org/en/pressrelease/2013/05/30/1720
organizations = ["The Cairo Institute for Human Rights Studies", "Misryon Against Religious Discrimination", "The Egyptian Coalition for the Rights of the Child", "Arab Program for Human Rights Activists", "Egyptian Association for Economic and Social Rights", "The Egyptian Association for Community Participation Enhancement", "Rural Development Association", "Mother Association for Rights and Development", "The Human Right Association for the Assistance of the Prisoners", "Arab Network for Human Rights Information", "The Egyptian Initiative for Personal Rights", "Initiators for Culture and Media", "The Human Rights Legal Assistance Group", "The Land Center for Human Rights", "The International Center for Supporting Rights and Freedoms", "Shahid Center for Human Rights", "Egyptian Center for Support of Human Rights", "The Egyptian Center for Public Policy Studies", "The Egyptian Center for Economic and Social Rights", "Andalus Institute for Tolerance and Anti-Violence Studies", "Habi Center for Environmental Rights", "Hemaia Center for Supporting Human Rights Defenders", "Social Democracy Studies Center", "The Hesham Mobarak Law Center", "Arab Penal Reform Organization", "Appropriate Communications Techniques for Development", "Forum for Women in Development", "Arab Penal Reform Organization", "The Egyptian Organization for Human Rights", "Tanweer Center for Development and Human Rights", "Better Life Association", "The Arab Foundation for Democracy Studies and Human Rights", "Arab Foundation for Civil Society and Human Right Support", "The New Woman Foundation", "Women and Memory Forum", "The Egyptian Foundation for the Advancement of Childhood Conditions", "Awlad Al Ard Association", "Baheya Ya Masr", "Association for Freedom of Expression and of Thought", "Center for Egyptian Women’s Legal Assistance", "Nazra for Feminist Studies"]

# Alternatively, use a list of id_article. This makes reading the database
# faster, since the script doesn't have to search for all the organizations.
# But it also means you have to make this list somehow, like this:
#   org_sql = ['article_content_no_punc LIKE "%'+org.lower()+'%"' for org in organizations]
#   sql_statement = 'SELECT id_article FROM articles WHERE '+' OR '.join(org for org in org_sql)

egind_ids = [13, 79, 193, 240, 241, 266, 271, 277, 300, 302, 311, 313, 334, 426, 556, 664, 710, 735, 750, 765, 773, 858, 899, 993, 1018, 1313, 1387, 1463, 1666, 1735, 1776, 1781, 1827, 1863, 1883, 1912, 1957, 1977, 2039, 2110, 2127, 2251, 2287, 2327, 2449, 2471, 2482, 2564, 2641, 2649, 2655, 2678, 2706, 2746, 2987, 3010, 3018, 3020, 3151, 3194, 3275, 3406, 3664, 3674, 3685, 3687, 3690, 3697, 3746, 3882, 3893, 3963, 4067, 4068, 4121, 4126, 4137, 4202, 4208, 4215, 4260, 4350, 4353, 4354, 4405, 4481, 4668, 4678, 4693, 4705, 4781, 4784, 4824, 4896, 5000, 5060, 5139, 5257, 5258, 5518, 5531, 5597, 5648, 5656, 5719, 5803, 5827, 5869, 5923, 5924, 5951, 5971, 5992, 5994, 5995, 5996, 6022, 6139, 6203, 6765, 6770, 6843, 6865, 6964, 7004, 7163, 7217, 7229, 7277, 7327, 7351, 7368, 7374, 7421, 7441, 7526, 7527, 7528, 7566, 7934, 7972, 7991, 8043, 8142, 8164, 8227, 8262, 8338, 8390, 8410, 8444, 8447, 8472, 8482, 8483, 8489, 8493, 8498, 8504, 8511, 8514, 8531, 8728, 8822, 8840, 8855, 8865, 8903, 8911, 8935, 9029, 9087, 9238, 9382, 9511, 9587, 9600, 9686, 9690, 9716, 9790, 10016, 10027, 10070, 10072, 10098, 10118, 10145, 10194, 10276, 10280, 10281, 10283, 10288, 10291, 10292, 10294, 10298, 10300, 10301, 10310, 10311, 10314, 10315, 10317, 10318, 10320, 10321, 10322, 10347, 10682, 10747, 10788, 10791, 10859, 11027, 11038, 11211, 11223, 11266, 11340, 11769, 11982, 12010, 12153, 12164, 12170, 12264, 12269, 12341, 12342, 12369, 12392, 12485, 12609, 12620, 12712, 12733, 12828, 12831, 12847, 12982, 13084, 13244, 13257, 13260, 13290, 13349, 13366, 13368, 13373, 13453, 13457, 13464, 13466, 13481, 13495, 13508, 13512, 13529, 13544, 13553, 13557, 13562, 13564, 13584, 13591, 13592]


#------------------------------------
# Connect to and query the database
#------------------------------------
conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
conn.row_factory = sqlite3.Row  # Use a dictionary cursor
c = conn.cursor()

# Query using the organization names
org_sql = ['article_content_no_punc LIKE "%'+org.lower()+'%"' for org in organizations]
sql_statement = 'SELECT * FROM articles WHERE '+' OR '.join(org for org in org_sql)
c.execute(sql_statement)

# Query using article ids
# sql_statement = ("""SELECT * FROM articles WHERE id_article IN ({0})""".format(', '.join('?' for _ in egind_ids)))
# c.execute(sql_statement, egind_ids)

# Fetch the results
ngo_mentions = c.fetchall()


#------------------------
# Parse parts of speech
#------------------------
# Initialize lists
global_adjectives = []
global_verbs = []

ngo_paragraph_adjs = []
ngo_paragraph_verbs = []

ngo_sentence_adjs = []
ngo_sentence_verbs = []

for row in ngo_mentions:  # Loop through all rows in the database results
  # Use TextBlob to parse the article
  # blob.tags returns the following parts of speech (some are missing, like VBN, etc.):
  #   noun (NN), adjective (JJ), determiner (DT), verb (VB), noun phrase (NP),
  #   sentence subject (SBJ), and prepositional noun phrase (PNP)
  blob = TextBlob(row['article_content_no_tags'])

  # Split the article into paragraphs
  paragraphs = (re.split('(\n)+', row['article_content_no_tags']))
  paragraphs = [paragraph for paragraph in paragraphs if paragraph != "\n"]
  paragraphs_lower = [paragraph.lower() for paragraph in paragraphs]

  # Get a list of all the paragraphs that mention one of the organizations
  paragraph_position = [i for i, x in enumerate(paragraphs_lower) if any(org.lower() in x for org in organizations)]

  # Split the article into sentences
  sentences_lower = [sentence.lower() for sentence in blob.sentences]
  # Get a list of all the sentences that mention one of the organizations
  sentence_position = [i for i, x in enumerate(sentences_lower) if any(org.lower() in x for org in organizations)]

  # Extract the adjectives and verbs from the paragraphs that mention
  # an organization and add them to the main lists
  for i in paragraph_position:
    par_blob = TextBlob(paragraphs[i])
    adjectives = [adj[0] for adj in par_blob.tags if adj[1] == 'JJ']
    verbs = [verb[0] for verb in par_blob.tags if 'VB' in verb[1]]
    ngo_paragraph_adjs.extend(adjectives)
    ngo_paragraph_verbs.extend(verbs)

  # Extract the adjectives and verbs from the sentences that mention an
  # organization and add them to the main lists
  for i in sentence_position:
    par_blob = blob.sentences[i]
    adjectives = [adj[0] for adj in par_blob.tags if adj[1] == 'JJ']
    verbs = [verb[0] for verb in par_blob.tags if 'VB' in verb[1]]
    ngo_sentence_adjs.extend(adjectives)
    ngo_sentence_verbs.extend(verbs)

  # Extract adjectives and verbs from the entire article and add them to the global lists
  adjectives = [adj[0] for adj in blob.tags if adj[1] == 'JJ']
  verbs = [verb[0] for verb in blob.tags if verb[1] == 'VB' or verb[1] == 'VBN']
  global_adjectives.extend(adjectives)
  global_verbs.extend(verbs)

#---------------------------
# Save lists to a csv file
#---------------------------
def write_to_csv(word_list, filename):
  with open(filename, 'w') as output_file:
    writer = csv.writer(output_file)
    writer.writerow(['word', 'frequency'])

    for row in Counter(word_list).most_common():
      writer.writerow(row)

write_to_csv(global_adjectives, publication_prefix + 'global_adjectives.csv')
write_to_csv(global_verbs, publication_prefix + 'global_verbs.csv')
write_to_csv(ngo_paragraph_adjs, publication_prefix + 'ngo_paragraph_adjs.csv')
write_to_csv(ngo_paragraph_verbs, publication_prefix + 'ngo_paragraph_verbs.csv')
write_to_csv(ngo_sentence_adjs, publication_prefix + 'ngo_sentence_adjs.csv')
write_to_csv(ngo_sentence_verbs, publication_prefix + 'ngo_sentence_verbs.csv')
#!/usr/bin/env python3

# Title:          export_to_mallet.py
# Description:    Create a folder of individual text files for every article that mentions an 
#                 NGO, to be used in MALLET 
# Author:         Andrew Heiss
# Last updated:   2014-03-13
# Python version: ≥3.0
# Usage:          Edit the three variables below and run the script. You'll need to run 
#                 the script for each publication. 

#-------------------
# Configure script
#-------------------
database = 'Corpora/egypt_independent.db'
prefix = 'egypt_independent'
output_folder = 'R/mallet_control'


#----------------------------------------------------------
# Import modules
import sqlite3
import random

# List of signatory organizations in http://www.eipr.org/en/pressrelease/2013/05/30/1720
organizations = ["The Cairo Institute for Human Rights Studies", "Misryon Against Religious Discrimination", "The Egyptian Coalition for the Rights of the Child", "Arab Program for Human Rights Activists", "Egyptian Association for Economic and Social Rights", "The Egyptian Association for Community Participation Enhancement", "Rural Development Association", "Mother Association for Rights and Development", "The Human Right Association for the Assistance of the Prisoners", "Arab Network for Human Rights Information", "The Egyptian Initiative for Personal Rights", "Initiators for Culture and Media", "The Human Rights Legal Assistance Group", "The Land Center for Human Rights", "The International Center for Supporting Rights and Freedoms", "Shahid Center for Human Rights", "Egyptian Center for Support of Human Rights", "The Egyptian Center for Public Policy Studies", "The Egyptian Center for Economic and Social Rights", "Andalus Institute for Tolerance and Anti-Violence Studies", "Habi Center for Environmental Rights", "Hemaia Center for Supporting Human Rights Defenders", "Social Democracy Studies Center", "The Hesham Mobarak Law Center", "Arab Penal Reform Organization", "Appropriate Communications Techniques for Development", "Forum for Women in Development", "The Egyptian Organization for Human Rights", "Tanweer Center for Development and Human Rights", "Better Life Association", "The Arab Foundation for Democracy Studies and Human Rights", "Arab Foundation for Civil Society and Human Right Support", "The New Woman Foundation", "Women and Memory Forum", "The Egyptian Foundation for the Advancement of Childhood Conditions", "Awlad Al Ard Association", "Baheya Ya Masr", "Association for Freedom of Expression and of Thought", "Center for Egyptian Women’s Legal Assistance", "Nazra for Feminist Studies"]


#------------------------------------
# Connect to and query the database
#------------------------------------
conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES)
conn.row_factory = sqlite3.Row  # Use a dictionary cursor
c = conn.cursor()

# Query using the organization names
org_sql = ['article_content_no_punc LIKE "%'+org.lower()+'%"' for org in organizations]
sql_statement = 'SELECT * FROM articles WHERE ('+' OR '.join(org for org in org_sql) + ') AND article_date BETWEEN \'2011-11-24 00:00:00\' AND \'2013-04-25 23:59:59\''
# c.execute(sql_statement)

# SQLite dosn't let you specify a seed for RANDOM() (using ORDER BY RANDOM()),
# so instead, we can sort by a hash of the id, multiplying by the id by a
# random decimal number and then ignoring everything before the decimal.
# Convoluted, but it works.
random.seed(1234)
pseudo_seed = random.random()
control_statement = 'SELECT * FROM articles WHERE article_date BETWEEN \'2011-11-24 00:00:00\' AND \'2013-04-25 23:59:59\' ORDER BY (substr(id_article * ' + str(pseudo_seed) + ' , length(id_article) + 2)) LIMIT 200'
c.execute(control_statement)

# Fetch the results
ngo_mentions = c.fetchall()


#------------------------------------
# Write each article to a text file
#------------------------------------
for row in ngo_mentions:
  filename = output_folder + '/' + prefix + '_' + str(row['id_article']) + '.txt'
  with open(filename, 'w') as f:
    f.write(row['article_title'] + '\n\n')
    # print(row['article_title'] + '\n\n')
    if row['article_subtitle']:
      f.write(row['article_subtitle'] + '\n\n')
    f.write(row['article_content_no_tags'])
    # print(row['article_content_no_tags'])

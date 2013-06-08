#!/usr/bin/env python3
# Import modules
import sqlite3

conn = sqlite3.connect(':memory:')
c = conn.cursor()

# Create sample database
c.execute("""CREATE TABLE authors (
  "id_author" integer PRIMARY KEY,
  "author_name" text NOT NULL
);""")
c.execute("""CREATE UNIQUE INDEX author_index ON authors (author_name);""")

# List of data to insert
authors = ['Sally', 'Fred', 'Jim']

# Insert everything
c.executemany("""INSERT OR IGNORE INTO authors (author_name) 
  VALUES (?)""", 
  [(author, ) for author in authors])  # Seems really convoluted

# Get the ids of all the authors
# The .format(.join()) combination adds the proper number of ?s to the SQL statement
c.execute("""SELECT id_author FROM authors 
  WHERE author_name IN ({0})""".format(', '.join('?' for _ in authors)), authors)
authors_in_db = c.fetchall()
author_ids = [author[0] for author in authors_in_db]
print(author_ids)

conn.commit()
conn.close()
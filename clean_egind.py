#!/usr/bin/env python3

# Title:          clean_files.py
# Description:    Filter a directory of HTML files, copying legitimate files to a new folder
#                 Necessary because Egypt Independent's Drupal installation served up multiple 
#                 versions of each page (probably because of Views), and httrack added a bunch 
#                 of temporary files
# Author:         Andrew Heiss
# Last updated:   2013-07-01
# Python version: ≥3.0
# Usage:          Edit the two variables below and run the script
#                 Manual hand-holding: I'm too lazy to programmatically filter out directories, 
#                   so the script chokes every time it comes across one. When that happens, just 
#                   delete the folder (and any corresponding folder.tmp or folder.html) files and
#                   run the script again. (Or add a check for directories or something :) )

#---------
# Set up
#---------
files_to_clean = 'egind_test/*'  # Must have trailing /*
folder_for_clean_files = 'egind_clean'  # Just the name of the folder (no trailing /)


# Import modules
from os import path, makedirs
from shutil import copy2
from glob import glob

# Strings to ignore (weird things added by Drupal and/or httrack in Egypt Independent)
ignore_these = ('.tmp', '2d85.html', 'b6c9.html', 'ed36.html')

# Make a list of just the clean HTML files
clean_file_list = [html_file for html_file in glob(files_to_clean) 
                    if not any(extension in html_file for extension in ignore_these)
                  ]

# Make the new folder
if not path.exists(folder_for_clean_files):
  makedirs(folder_for_clean_files)

# Copy files to the new folder
for clean_file in clean_file_list:
  copy2(clean_file, folder_for_clean_files)

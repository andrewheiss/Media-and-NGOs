#!/usr/bin/env python3
# Import modules
from os import path, makedirs
from shutil import copy2
from glob import glob

# Set up
files_to_clean = 'egind_test/*'  # Must have trailing /*
folder_for_clean_files = 'egind_clean'  # Just the name of the folder

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

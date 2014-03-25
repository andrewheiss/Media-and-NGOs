#!/usr/bin/env python3

# Title:          clean_dne.py
# Description:    Flatten the complex nested folder stucture made by WordPress and rename 
#                 all the corresponding `index.html` files accordingly. 
#                 Copy site_dump/2010/03/11/post-title/index.html 
#                 to folder_for_clean_files/2010_03_11_post-title.html
# Author:         Andrew Heiss
# Last updated:   2013-07-05
# Python version: ≥3.0
# Usage:          Edit the two variables below and run the script.
# Issues:         * The script is made to use relative folders. If you use an absolute folder 
#                   for `nested_folders` the renamed files will use the full page (i.e. 
#                   users_andrew_desktop_folder_2010/06/03/page.html), which is ugly. It's best 
#                   to copy this script into a folder one step below the year-based folders. 
#                   For example:
#
#                   clean_dne.py
#                   articles/
#                   --2009/
#                   --2010/
#                   --...
#
#                 * Each year has an additional folder named `page`. Remove them manually.
#                 * On January 28, 2013 there was a photo gallery (photo-gallery-same-day-different-rage) 
#                   that was posted as an article and thus doesn't follow the same folder structure. Delete it manually.

#---------
# Set up
#---------
nested_folders = 'dne_test'
folder_for_clean_files = 'dne_clean'

# Import modules
import os
from shutil import copy2

# Make the new folder
if not os.path.exists(folder_for_clean_files):
  os.makedirs(folder_for_clean_files)

# Copy renamed files to folder
for root, dirs, files in os.walk(nested_folders):
  nested_levels = root.split(os.sep)  # Split the root by '/' (POSIX) or '\' (Windows)
  if len(nested_levels) == 5:
    del dirs[:]  # Get rid of deeper nested folders to prevent unnecessary directory walking
    index_file = files[files.index('index.html')]  # Get the only index.html file (in case there are other files that slipped in)
    original_filename = os.path.join(root, index_file)  # Full relative path of index file
    new_filename = '_'.join(nested_levels[1:]) + '.html'  # New _-separated file name
    copy2(original_filename, folder_for_clean_files + os.sep + new_filename)  # Move file to folder for clean files

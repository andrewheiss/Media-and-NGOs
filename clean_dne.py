#!/usr/bin/env python3

nested_folders = 'dne_test'
folder_for_clean_files = 'dne_clean'

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

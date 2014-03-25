#!/usr/bin/env sh

# DON'T RUN THIS WHOLE SCRIPT ALL AT ONCE! Just copy/paste individual lines.

# The best way to get all the articles for all these sites was to brute force
# download everything with a spider and then parse it all with BeautifulSoup
# in Python. Because it took days to crawl through the sites, it was most
# efficient to:
#   1. Create a temporary virtual cloud server at DigitalOcean.com
#      (cheaper than Amazon's EC2)
#   2. Install httrack (sudo apt-get install httrack)
#   3. Let it run forever (expanding image if necessary)
#   4. Zip it up (tar -zcvf blah.tar.gz blah)
#   5. Download it over SFTP
#   6. Destroy cloud instance

# Random attempts at getting wget to work. None of these ended up working, though.
# wget -mkcb -w 2 --random-wait --reject=jpg,jpeg,gif,png,tif http://www.dailynewsegypt.com/
# wget -rcb -w 2 --random-wait --reject=jpg,jpeg,gif,png,tif --no-parent http://www.dailynewsegypt.com/2013/01
# wget -mkb -w 2 --random-wait --reject=jpg,jpeg,gif,png,tif --exclude-directories=/UI/ http://english.ahram.org.eg/
# wget -r -l10 -b -w 1 -nv --random-wait --reject=jpg,jpeg,gif,png,tif \ 
# --exclude-directories=/UI/ --output-file=urllist.txt \ 
# http://english.ahram.org.eg/

# httrack commands (these actually did work), though they probably overlogged
# everything. For some reason it was impossible to pipe the verbose output to
# the log.txt file. Only this command made any sort of log (at blah/hts-
# log.txt). Directing output to log.txt helped force httrack to the
# background, which it struggled to do otherwise.
httrack "http://english.ahram.org.eg" -O "./blah" http://english.ahram.org.eg +*.css +*.js -english.ahram.org.eg/UI* -*.gif -*.jpg -*.png -*.tif -*.bmp --verbose --extra-log --file-log --single-log -#L1000000 > log.txt &

httrack "http://www.dailynewsegypt.com" -O "./blah" http://www.dailynewsegypt.com +*.css +*.js -*.gif -*.jpg -*.png -*.tif -*.bmp --verbose --extra-log --file-log --single-log -#L1000000 > log.txt &

httrack "http://www.egyptindependent.com" -O "./blah" http://www.egyptindependent.com +*.css +*.js -*.gif -*.jpg -*.png -*.tif -*.bmp --verbose --extra-log --file-log --single-log -#L1000000 > log.txt &


# To make things simpler, divide all the HTML files for Ahram and Egypt
# Independent into subfolders (with 2000 articles) with this one liner:
ls|xargs -n2000|awk ' {i++; system("mkdir dir"i); system("mv "$0" -t dir"i)}'

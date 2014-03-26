## Discovering Discourse: The Relationship between Media and NGOs in Egypt between 2011--13

[Ken Rogerson](http://fds.duke.edu/db/Sanford/rogerson) • Sanford School of Public Policy • Duke University  
[Andrew Heiss](http://www.andrewheiss.com/) • Sanford School of Public Policy • Duke University

---

## Abstract

Forthcoming...


## Data

The data for this project consists of all articles published by [Al-Ahram English](http://english.ahram.org.eg/), [Daily News Egypt](http://www.dailynewsegypt.com/), and [Egypt Independent](http://www.egyptindependent.com/) between November 24, 2011 and April 25, 2013. We essentially used multiple virtual private servers to download local mirrors of their sites using a combination of [`httrack`](http://www.httrack.com/) and `wget`, and then used [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) in Python to extract all the data into an SQLite database. 

For the sake of transparency, the files for scraping and parsing are in `parse_raw_html/`. However, because the whole process took weeks (and a lot of manual corrections), none of those files are included in the `Makefile`. Instead, the `Makefile` assumes you have copies of the complete, clean SQLite corpora. 

Because the corpora are fairly large (160–500 MB), and because of potentially murky intellectual property issues, we have not included them in this repository. If you are interested in replicating, extending, or playing around with this project, contact [Andrew Heiss](mailto:andrew.heiss@duke.edu) to get access to the corpora.


## Usage

Forthcoming...


## Prerequisites

### OS X and Linux

Forthcoming...

### Windows

Forthcoming...

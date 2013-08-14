# Title:          load_data.R
# Description:    Load all corpus data into R, clean it up, save as .RData file for later use
# Author:         Andrew Heiss
# Last updated:   2013-08-13
# R version:      ≥3.0

# Load packages
library(RSQLite)
library(lubridate)


#--------------
# Import data
#--------------
drv <- dbDriver("SQLite") 
egind.con <- dbConnect(drv, "/Users/andrew/Dropbox/Media and NGOs in the ME/Media and NGOs/Corpora/egypt_independent.db") 
egind.articles <- dbGetQuery(egind.con, "SELECT * FROM articles WHERE article_word_count < 10000")  # Ignore new constitution
ahram.con <- dbConnect(drv, "/Users/andrew/Dropbox/Media and NGOs in the ME/Media and NGOs/Corpora/ahram.db") 
ahram.articles <- dbGetQuery(ahram.con, "SELECT * FROM articles")
dne.con <- dbConnect(drv, "/Users/andrew/Dropbox/Media and NGOs in the ME/Media and NGOs/Corpora/dne.db") 
dne.articles <- dbGetQuery(dne.con, "SELECT * FROM articles")


#----------------
# Clean up data
#----------------
# There's probably a better way to do this, like with a function or something. But when I use
# add.dates <- function(dataset) {
#   dataset$actual_date <- as.POSIXct(dataset$article_date, tz="EET")
#   ...
#   return(dataset)
# }
# R hangs indefinitely, since it's copying the whole huge dataset into memory 1+ times.
# So in the meantime, lots of repetition! :)

# Add dates
egind.articles$actual_date <- as.POSIXct(egind.articles$article_date, tz="EET")
egind.articles$month <- floor_date(egind.articles$actual_date, "month")
egind.articles$week <- floor_date(egind.articles$actual_date, "week")
egind.articles$day <- floor_date(egind.articles$actual_date, "day")

ahram.articles$actual_date <- as.POSIXct(ahram.articles$article_date, tz="EET")
ahram.articles$month <- floor_date(ahram.articles$actual_date, "month")
ahram.articles$week <- floor_date(ahram.articles$actual_date, "week")
ahram.articles$day <- floor_date(ahram.articles$actual_date, "day")

dne.articles$actual_date <- as.POSIXct(dne.articles$article_date, tz="EET")
dne.articles$month <- floor_date(dne.articles$actual_date, "month")
dne.articles$week <- floor_date(dne.articles$actual_date, "week")
dne.articles$day <- floor_date(dne.articles$actual_date, "day")


#-----------------------------------
# Create subsets that mention NGOs
#-----------------------------------
ngos <- tolower(c("The Cairo Institute for Human Rights Studies", "Misryon Against Religious Discrimination", "The Egyptian Coalition for the Rights of the Child", "Arab Program for Human Rights Activists", "Egyptian Association for Economic and Social Rights", "The Egyptian Association for Community Participation Enhancement", "Rural Development Association", "Mother Association for Rights and Development", "The Human Right Association for the Assistance of the Prisoners", "Arab Network for Human Rights Information", "The Egyptian Initiative for Personal Rights", "Initiators for Culture and Media", "The Human Rights Legal Assistance Group", "The Land Center for Human Rights", "The International Center for Supporting Rights and Freedoms", "Shahid Center for Human Rights", "Egyptian Center for Support of Human Rights", "The Egyptian Center for Public Policy Studies", "The Egyptian Center for Economic and Social Rights", "Andalus Institute for Tolerance and Anti-Violence Studies", "Habi Center for Environmental Rights", "Hemaia Center for Supporting Human Rights Defenders", "Social Democracy Studies Center", "The Hesham Mobarak Law Center", "Arab Penal Reform Organization", "Appropriate Communications Techniques for Development", "Forum for Women in Development", "Arab Penal Reform Organization", "The Egyptian Organization for Human Rights", "Tanweer Center for Development and Human Rights", "Better Life Association", "The Arab Foundation for Democracy Studies and Human Rights", "Arab Foundation for Civil Society and Human Right Support", "The New Woman Foundation", "Women and Memory Forum", "The Egyptian Foundation for the Advancement of Childhood Conditions", "Awlad Al Ard Association", "Baheya Ya Masr", "Association for Freedom of Expression and of Thought", "Center for Egyptian Women’s Legal Assistance", "Nazra for Feminist Studies"))

egind.ngos <- egind.articles[grepl(paste(ngos, collapse="|"), egind.articles$article_content_no_punc),]
ahram.ngos <- ahram.articles[grepl(paste(ngos, collapse="|"), ahram.articles$article_content_no_punc),]
dne.ngos <- dne.articles[grepl(paste(ngos, collapse="|"), dne.articles$article_content_no_punc),]


#-----------------
# Save for later
#-----------------
rm(drv, ahram.con, dne.con, egind.con)
save(file="media_data.RData", list=ls(all=TRUE))
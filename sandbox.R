library(RSQLite)
library(sqldf)


# sqldf way
# blah <- sqldf('SELECT * FROM articles', dbname = '/Users/andrew/Dropbox/Media and NGOs in the ME/Media and NGOs data/egypt_independent.db')

# RSQLite way
drv <- dbDriver("SQLite") 
con <- dbConnect(drv, "/Users/andrew/Dropbox/Media and NGOs in the ME/Media and NGOs data/egypt_independent.db") 
# articles <- dbReadTable(con, "articles") 
articles <- dbGetQuery(con, "SELECT * FROM articles WHERE article_word_count < 10000")  # Ignore new constitution

hist(articles$article_word_count)
max(articles$article_word_count)
head(sort(articles$article_word_count, decreasing=TRUE))

articles$article_date1 <- ts(articles$article_date)


library(RSQLite)
library(lubridate)
library(plyr)
library(stringr)

# sqldf way
# blah <- sqldf('SELECT * FROM articles', dbname = '/Users/andrew/Dropbox/Media and NGOs in the ME/Media and NGOs data/egypt_independent.db')

# RSQLite way
drv <- dbDriver("SQLite") 
con <- dbConnect(drv, "/Users/andrew/Dropbox/Media and NGOs in the ME/Media and NGOs/Corpora/dne.db") 
# articles <- dbReadTable(con, "articles") 
articles <- dbGetQuery(con, "SELECT * FROM articles WHERE article_word_count < 10000")  # Ignore new constitution

articles$actual_date <- as.POSIXct(articles$article_date, tz="EET")

# Using zoo and aggregate
# library(chron)
# library(zoo)
# articles$dummy <- 1
# z <- zoo(articles$dummy, order.by=as.chron(as.character(dt$article_date)))
# z.aggregated <- aggregate(z, function(x) as.POSIXct(trunc(x,"day")) )
# plot(z.aggregated)

# Using lubridate
articles$month <- floor_date(articles$actual_date, "month")
articles$week <- floor_date(articles$actual_date, "week")
articles$day <- floor_date(articles$actual_date, "day")

publishing_monthly <- ddply(articles, "month", summarise, x=length(month))

wc_monthly <- ddply(articles, "month", summarise, x=sum(article_word_count))
plot(wc_monthly[-nrow(wc_monthly),], type="l")

publishing_weekly <- ddply(articles, "week", summarise, x=length(week))
publishing_daily <- ddply(articles, "day", summarise, x=length(day))

plot(publishing_monthly[-nrow(publishing_monthly),], type="l")
plot(publishing_daily, type="l")
plot(publishing_weekly[-nrow(publishing_weekly),], type="l")


ngos <- tolower(c("The Cairo Institute for Human Rights Studies", "Misryon Against Religious Discrimination", "The Egyptian Coalition for the Rights of the Child", "Arab Program for Human Rights Activists", "Egyptian Association for Economic and Social Rights", "The Egyptian Association for Community Participation Enhancement", "Rural Development Association", "Mother Association for Rights and Development", "The Human Right Association for the Assistance of the Prisoners", "Arab Network for Human Rights Information", "The Egyptian Initiative for Personal Rights", "Initiators for Culture and Media", "The Human Rights Legal Assistance Group", "The Land Center for Human Rights", "The International Center for Supporting Rights and Freedoms", "Shahid Center for Human Rights", "Egyptian Center for Support of Human Rights", "The Egyptian Center for Public Policy Studies", "The Egyptian Center for Economic and Social Rights", "Andalus Institute for Tolerance and Anti-Violence Studies", "Habi Center for Environmental Rights", "Hemaia Center for Supporting Human Rights Defenders", "Social Democracy Studies Center", "The Hesham Mobarak Law Center", "Arab Penal Reform Organization", "Appropriate Communications Techniques for Development", "Forum for Women in Development", "Arab Penal Reform Organization", "The Egyptian Organization for Human Rights", "Tanweer Center for Development and Human Rights", "Better Life Association", "The Arab Foundation for Democracy Studies and Human Rights", "Arab Foundation for Civil Society and Human Right Support", "The New Woman Foundation", "Women and Memory Forum", "The Egyptian Foundation for the Advancement of Childhood Conditions", "Awlad Al Ard Association", "Baheya Ya Masr", "Association for Freedom of Expression and of Thought", "Center for Egyptian Women’s Legal Assistance", "Nazra for Feminist Studies"))
ngos.simple <- tolower(c(" NGO"))

egind <- articles[grepl(paste(ngos, collapse="|"), articles$article_content_no_punc),]

egind.small <- egind[sample(nrow(egind), 50),]
egind.small <- egind.small[, c('id_article', 'article_title', 'article_date', 'article_url', 'article_type', 'article_content_no_tags', 'article_translated')]
write.csv(egind.small, "dne.csv")

# id_article, article_title, article_date, article_url, article_type, article_content_no_tags, article_translated

test.ngos <- articles[grepl(paste(ngos.simple, collapse="|"), articles$article_content_no_punc),]

test_monthly <- ddply(test, "month", summarise, x=length(month))
plot(test_monthly)

test.ngos_monthly <- ddply(test.ngos, "month", summarise, x=length(month))
plot(test.ngos_monthly)



subset(articles, article_content_no_punc %in% ngos)


articles$article_content_no_punc %in% ngos


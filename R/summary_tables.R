# Title:          summary_tables.R
# Description:    Generate corpus summary tables
# Author:         Andrew Heiss
# Last updated:   2013-12-24
# R version:      ≥3.0

# Libraries
library(xtable)

# Set working directory
base.directory <- "~/Dropbox/Media and NGOs in the ME/Media and NGOs/R"
setwd(base.directory)

# Load corpus
load("media_data.RData")

# Format
table.format <- "latex"  # Either html or latex


#-------------------------
# Generate summary table
#-------------------------
# This would probably be done in like one line with plyr, but it's harder to
# deal with multiple dataframes for all articles + NGO mentions. 
summarize.data <- function(df.all, df.ngos) {
  num.articles <- nrow(df.all)
  num.words <- sum(df.all$article_word_count)
  num.articles.ngos <- nrow(df.ngos)
  num.words.ngos <- sum(df.ngos$article_word_count)
  proportion.articles.ngos <- num.articles.ngos / num.articles
  return(data.frame(num.articles, num.words, num.articles.ngos, num.words.ngos, proportion.articles.ngos))
}

# Build table
table.output <- rbind(summarize.data(ahram.articles, ahram.ngos),
                      summarize.data(dne.articles, dne.ngos),
                      summarize.data(egind.articles, egind.ngos))
table.output <- rbind(table.output, colSums(table.output))

# Fix total proportion cell, since it's not just the sum of the other rows
table.output[4,5] <- table.output[4,3] / table.output[4,1]

# Add pretty names
publication.rows <- c("Al-Ahram English", "Daily News Egypt", "Egypt Independent", "Total")
table.output <- cbind(publication=publication.rows, table.output)
header.names <- c("Publication", "Number of articles", "Number of words", 
                  "Number of articles that mention NGOs", "Number of words in articles that mention NGOs",
                  "Proportion of NGO articles")
colnames(table.output) <- header.names

# Pretty output
print(xtable(prettyNum(table.output, big.mark=",", digits=4)), type=table.format)

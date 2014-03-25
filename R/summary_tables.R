# Title:          summary_tables.R
# Description:    Generate summary tables
# Author:         Andrew Heiss
# Last updated:   2014-03-25
# R version:      ≥3.0

# Libraries
library(pander)

# Process command line arguments
source("get_args.R")  # Better handling of arguments
args <- getArgs(defaults=list(control=FALSE))
control = args$control

# Set appropriate variables
if(control == FALSE) {
  model.data <- "../Output/topic_model.RData"
  table.name <- "../Output/table_topic_model.md"
} else {
  model.data <- "../Output/topic_model_control.RData"
  table.name <- "../Output/table_topic_model_control.md"
}


#-----------------------------
# Output corpus-based tables
#-----------------------------
if(control == FALSE) {
  # Load corpus data
  load("../Output/media_data.RData")

  #-------------------------
  # Generate summary table
  #-------------------------
  # This would probably be done in like one line with plyr, but it's harder to
  # deal with multiple dataframes for all articles + NGO mentions. 
  summarize.data <- function(df.all, df.ngos) {
    num.articles <- nrow(df.all)
    #num.words <- sum(df.all$article_word_count)
    num.articles.ngos <- nrow(df.ngos)
    num.words.ngos <- sum(df.ngos$article_word_count)
    proportion.articles.ngos <- num.articles.ngos / num.articles
    #return(data.frame(num.articles, num.words, num.articles.ngos, proportion.articles.ngos))
    return(data.frame(num.articles, num.articles.ngos, proportion.articles.ngos))
  }

  # Build table
  table.output <- rbind(summarize.data(ahram.articles, ahram.ngos),
                        summarize.data(dne.articles, dne.ngos),
                        summarize.data(egind.articles, egind.ngos))
  table.output <- rbind(table.output, colSums(table.output))

  # Fix total proportion cell, since it's not just the sum of the other rows
  # table.output[4,4] <- table.output[4,3] / table.output[4,1]
  table.output[4,3] <- table.output[4,2] / table.output[4,1]

  # Format as percent
  table.output$proportion.articles.ngos <- paste(formatC(100 * table.output$proportion.articles.ngos, format="f", digits=2), "%", sep = "")

  # Add pretty names
  publication.rows <- c("Al-Ahram English", "Daily News Egypt", "Egypt Independent", "Total")
  table.output <- cbind(publication=publication.rows, table.output)
  header.names <- c("Publication", "Articles", #"Words", 
                    "Articles (NGOs)", "NGO articles (%)")
  colnames(table.output) <- header.names


  #-------------------
  # Export summaries
  #-------------------
  # Markdown
  cat(pandoc.table.return(table.output, split.tables=Inf, 
                          emphasize.strong.rows=4, big.mark=",", digits=4,
                          justify="center", caption="Summary of corpus and subset"),
      file="../Output/table_corpus_summary.md")


  #----------------------
  # Export list of NGOs
  #----------------------
  # Add enough NAs to coerce list into a matrix
  num.columns <- 3
  cells.to.add <- num.columns - (length(ngos) %% num.columns)
  ngo.output <- matrix(c(sort(ngos), rep(NA, cells.to.add)), ncol=num.columns, byrow=TRUE)

  # Markdown
  cat(pandoc.table.return(ngo.output, split.tables=Inf, 
                          justify="left", caption="List of NGOs"),
      file="../Output/table_ngo_list.md")
}

#----------------------
# Topic model summary
#----------------------
load(model.data) 
topic.summary <- topic.keys.result[c("dirichlet", "topic.words", "short.names")]
topic.summary <- topic.summary[order(topic.summary$dirichlet, decreasing=TRUE), ]
colnames(topic.summary) <- c("Dirichlet α", "Top ten words", "Short name")
rownames(topic.summary) <- paste(" ", 1:nrow(topic.summary))  # To trick pander into thinking these are real rownames...

# Pandoc Markdown
cat(pandoc.table.return(topic.summary, split.tables=Inf, digits=3,
                        justify="left", caption="Topic model summary"), 
    file=table.name)

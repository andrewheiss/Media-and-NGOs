# Title:          manual_topic_validation.R
# Description:    Select random articles from the topic model, graph their topics, and output their content
# Author:         Andrew Heiss
# Last updated:   2013-12-26
# R version:      ≥3.0

# Load libraries and set variables
library(plyr)
library(ggplot2)
library(scales)
library(reshape2)

seed <- 1234
num.articles <- 3

load("topic_model.RData")
load("media_data.RData")


# Sample from the un-normalized topic model
set.seed(seed)
validation <- topic.docs[sample(nrow(topic.docs), num.articles), ]
validation$article <- factor(regmatches(row.names(validation), regexpr("^[^\\.]+", row.names(validation))))
validation.long <- melt(validation, id="article", variable.name="topic", value.name="proportion")
validation.long$label <- factor(validation.long$topic, labels=topic.keys.result$short.names)


# Plot the topic proportions for sampled articles 
p <- ggplot(validation.long, aes(x=label, y=proportion))
p + geom_bar(stat="identity") + coord_flip() + facet_wrap(~ article) + 
  scale_y_continuous(labels=percent) + 
  labs(x=NULL, y=NULL) + theme_bw()


# Extract articles from the corpus
get.article <- function(publication.id) {
  article.id <- as.integer(gsub("\\D", "", publication.id))  
  corpus.name <- regmatches(publication.id, regexpr("^[^_]+", publication.id))
  
  if(corpus.name == "ahram") {
    corpus <- ahram.ngos
  } else if (corpus.name == "dne") {
    corpus <- dne.ngos
  } else if (corpus.name == "egypt") {
    corpus <- egind.ngos
  }
  
  return(corpus[corpus$id_article==article.id, ])
}

full.text <- ldply(lapply(validation$article, FUN=get.article), data.frame)


# Print articles to file
pretty.print.article <- function(x) {
  cat("\n")
  cat("ID: ", x["id_article"], " (", x["publication"], ")\n\n", sep="")
  cat("Title:", x["article_title"], "\n\n")
  cat("Subtitle:", x["article_subtitle"], "\n\n")
  cat("Date:", x["article_date"], "\n\n")
  cat("URL:", x["article_url"], "\n\n")
  cat("Word count:", x["article_word_count"], "\n\n")
  cat("Type:", x["article_type"], "\n\n")
  cat("Article:\n", x["article_content_no_tags"])
  cat("\n\n\n--------------------\n\n") 
}

sink("../Output/validation-articles.txt")
apply(full.text, MARGIN=1, FUN=pretty.print.article)
sink(file=NULL)


#-----------------------------------------------------------------------
# Get the topics assigned to each of the words in the sampled articles
#-----------------------------------------------------------------------
# Read the huge words database 
# TODO: Make this more dynamic, since `topic-state.gz` is actually user configurable in `load_data.R`
everything <- read.table("topic-state.gz")
colnames(everything) <- c("doc", "source.file", "pos", "typeindex", "type", "topic")

# Build list of filenames to select
full.text$publication <- ifelse(full.text$publication == "egind", "egypt_independent", full.text$publication)
articles.to.select <- paste("mallet_input/", full.text$publication, "_", full.text$id_article, ".txt", sep="")

# Select them
article.words <- subset(everything, everything$source.file %in% articles.to.select)
rm(everything)  # Get rid of huge data frame

# Merge the word data frame with the human-readable topics
article.words$order <- 1:nrow(article.words)  # Add a column for the order, since merge kills the order
combined <- merge(article.words, topic.keys.result, by.x="topic", by.y="key", sort=TRUE)  # Merge
combined <- combined[order(combined$order), ]  # Reorder

# Better column order
combined <- combined[c("source.file", "doc", "pos", "typeindex", "type", "short.names", "topic.words")]

# Save to a file
write.csv(x=combined, file="../Output/topic-words.csv", row.names=FALSE)

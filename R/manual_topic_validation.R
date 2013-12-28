# Title:          manual_topic_validation.R
# Description:    Select random articles from the topic model, graph their topics, and output their content
# Author:         Andrew Heiss
# Last updated:   2013-12-26
# R version:      ≥3.0

# Load libraries and set variables
library(plyr)
library(ggplot2)
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
  cat("ID: ", x["id_article"], " (", x["publication"], ")\n\n", sep="")
  cat("Title:", x["article_title"], "\n\n")
  cat("Subtitle:", x["article_subtitle"], "\n\n")
  cat("Date:", x["article_date"], "\n\n")
  cat("URL:", x["article_url"], "\n\n")
  cat("Word count:", x["article_word_count"], "\n\n")
  cat("Type:", x["article_type"], "\n\n")
  cat("Article:\n", x["article_content_no_tags"])
  cat("\n\n\n--------------------\n\n\n") 
}

sink("validation_articles.txt")
apply(full.text, MARGIN=1, FUN=pretty.print.article)
sink(file=NULL)

# Title:          create_topic_model.R
# Description:    Build topic model with MALLET
# Author:         Andrew Heiss
# Last updated:   2014-03-13
# R version:      ≥3.0

# Load libraries and set initial working directory
library(reshape2)
library(scales)
library(plyr)
library(pander)

mallet.seed <- 1234

base.directory <- "~/Dropbox/Media and NGOs in the ME/Media and NGOs/R"
setwd(base.directory)

# Make sure MALLET is there
if(!file.exists("mallet/bin/mallet")) {
  stop("MALLET not found. You need to place MALLET in a subfolder named 'mallet' in the same directory as this file.")
}


#------------------------
# Create MALLET command
#------------------------
# Folder with input text files
# TODO: Make this work with spaces. shQuote(file.path(importdir)) should work, but the quoted path breaks MALLET
import.dir <- "mallet_stemmed"

# Set names for output files 
output.file <- "topics.mallet"  # MALLET data file
output.state <-  "topic-state.gz"  # List of every word in every article and which topics they're assigned to
output.topickeys <- "topic-keys.txt"  # List of the topics
output.doctopics <- "topic-doctopics.txt"  # Proportion of each topic in each input file

# "Control" group of articles
# import.dir <- "mallet_control_stemmed"

# Set names for output files 
# output.file <- "topics.mallet_control"  # MALLET data file
# output.state <-  "topic-state_control.gz"  # List of every word in every article and which topics they're assigned to
# output.topickeys <- "topic-keys_control.txt"  # List of the topics
# output.doctopics <- "topic-doctopics_control.txt"  # Proportion of each topic in each input file

# Topic and optimization options
num.topics <- 20  # Number of topics to model
num.iterations <- 1000  # Number of training/learning Gibbs sampling iterations
num.top.words <- 11  # Number of most probable words to print (num.top.words - 1 words, actually)
optimize.interval <- 20  # Number of iterations between reestimating dirichlet hyperparameters
optimize.burnin <- 50  # Number of iterations to run before first estimating dirichlet hyperparameters

# Finally, paste the commands together
cd <- paste("cd", shQuote(normalizePath(base.directory)))
import.command <- paste("mallet/bin/mallet", "import-dir", "--input", import.dir, 
                        "--output", output.file, 
                        "--keep-sequence", 
                        "--token-regex \"\\w+\"", sep=" ")  # token-regex will consider _ as part of the word
train.command <- paste("mallet/bin/mallet", "train-topics", "--input", output.file,
                       "--num-iterations", num.iterations,
                       "--num-topics", num.topics,
                       "--num-top-words", num.top.words, 
                       "--optimize-interval", optimize.interval, 
                       "--optimize-burn-in", optimize.burnin, 
                       "--output-state", output.state, 
                       "--output-topic-keys", output.topickeys, 
                       "--output-doc-topics", output.doctopics, 
                       "--random-seed", mallet.seed, sep=" ")

# And run them all at the same time
mallet.command <- paste(cd, import.command, train.command, sep=" ; ")
system(mallet.command)


#--------------------
# Parse the results
#--------------------
# Read the files created by MALLET
topic.keys.result <- read.table(output.topickeys, header=F, sep="\t")
doc.topics.result <- read.table(output.doctopics, header=F, sep="\t")

# MAYBE: Make this *actually* look for (and remove?) the .DS_Store file?
# if(nrow(doc.topics.result) != 515) {
#   stop("MALLET accidentally parsed an extra file (like .DS_Store). Delete it manually and rerun this file.")
# }

# doc.topics.result comes in the following format:
#
#   id  file              topic   proportion    topic   proportion    ...
#   0   ahram_17539.txt   17      0.400385      12      0.3308976     ...
#   1   ahram_17989.txt   21      0.4516575     13      0.1848781     ...
#   ...
#
# The reshape() and acast() commands below covert that form to the 
# following matrix, with columns for each topic:
#
#   row.name          0      1      2      ...
#   ahram_17539.txt   0.014  0.007  0.076  ...
#   ahram_17989.txt   0.005  0.006  0.129  ...
#   ...
dat <- doc.topics.result
doc.topics.long <- reshape(dat, idvar=1:2, varying=list(topics=colnames(dat[,seq(3, ncol(dat)-1, 2)]), 
                          props=colnames(dat[,seq(4, ncol(dat), 2)])), direction="long")
doc.topics <- acast(doc.topics.long, V2 ~ V3, value.var="V4")
row.names(doc.topics) <- basename(row.names(doc.topics))
rm(doc.topics.long, dat)  # Get rid of these extra data frames

# Normalize topic percentages so that the proportion of articles in each topic sums to 100%
normalize.topics <- function(x) {
  x.norm <- t(x)  # Transpose
  x.norm <- x.norm / rowSums(x.norm)  # Divide by row sums
  return(data.frame(t(x.norm)))  # Re-transpose
}

# Example:
#           Regular                       Normalized        
# ---------------------------    ---------------------------
#        topic0 topic1 topic2           topic0 topic1 topic2
# ahram1    0.4    0.1    0.5    ahram1    0.4  0.143  0.385
# dne1      0.1    0.3    0.6    dne1      0.1  0.429  0.462
# egind1    0.5    0.3    0.2    egind1    0.5  0.429  0.154 

# Check on actual data
# colSums(doc.topics)  # Definitely not 100% in each topic
# colSums(normalize.topics(doc.topics))  # Definitely 100% in each topic

# Make clean data frames of topic proportions
topic.docs <- data.frame(doc.topics)  # Regular
topic.docs.norm <- normalize.topics(doc.topics)  # Normalized


# Example normalized table
example.normal <- data.frame(topic1=c(0.5, 0.1, 0.5), topic2=c(0.0, 0.3, 0.3), topic3=c(0.5, 0.6, 0.2))
rownames(example.normal) <- c("Article 1", "Article 2", "Article 3")
example.normalized <- normalize.topics(example.normal)

# Add total rows and columns
example.normal$total <- rowSums(example.normal)
example.normal <- rbind(example.normal, colSums(example.normal))
rownames(example.normal)[4] <- "Column totals"
colnames(example.normal)[4] <- "Row totals"
example.normal[4,4] <- NA  # Remove column/row sum

example.normalized$total <- rowSums(example.normalized)
example.normalized <- rbind(example.normalized, colSums(example.normalized))
rownames(example.normalized)[4] <- "Column totals"
colnames(example.normalized)[4] <- "Row totals"
example.normalized[4,4] <- NA  # Remove column/row sum

# Combine tables into mega table
example.combined <- cbind(example.normal, "", example.normalized)
colnames(example.combined)[5] <- "→"

# Export to Markdown
cat(pandoc.table.return(example.combined, split.tables=Inf, 
                        justify="center", digits=2),
    file="../Output/table_norm_example.md")


#-----------------------------
# Add short names for topics
#-----------------------------
colnames(topic.keys.result) <- c("key", "dirichlet", "topic.words")
# SPSA short names
# short.names <- c("National government", "Draft constitution", "Environmental issues",
#                  "Development", "Police arrests", "Protests and clashes", 
#                  "Sexual violence", "Police torture", "Elections", "Human rights and civil society", 
#                  "Post-revolutionary Egypt", "Business and government", "Egyptian workers", 
#                  "Trials", "Religious issues", "Legislation", "Morsi and press freedom",
#                  "SCAF", "Youth in the street", "Christian issues")

# Shortnames for enhanced corpus (stemmed, n-grammed)
short.names <- c("Police torture", "Sexual violence", "Media and censorship", 
                 "Sectarian issues", "Egyptian workers", "Religious issues", 
                 "Police violence", "Business", "Protests and clashes", 
                 "Muslim Brotherhood and constitution", "Elections", "Military trials", 
                 "Legislation and governance", "Environmental issues", 
                 "Human rights and civil society", "Protestors and activism", 
                 "Public economics", "Police arrests", "Muslim Brotherhood and politics", 
                 "Post-revolutionary Egypt (catch-all)")
topic.keys.result$short.names <- short.names

# Control group short names
# short.names <- c("Muslim Brotherhood and politics", "Morsi and the media", 
#                  "Miscellaneous", "Unions and strikes", "Trials", "Egypt (catch-all)", 
#                  "Religious issues", "Syrian civil war", "Cairo affairs", 
#                  "Israel-Palestinian conflict", "Protests", "Foreign affairs", 
#                  "Christian affairs", "Football", "Culture", "Regional violence", 
#                  "Tourism", "Oil", "Social affairs", "Public economics")
# topic.keys.result$short.names <- short.names


#------------------
# Save everything
#------------------
save(topic.keys.result, topic.docs, topic.docs.norm, file="topic_model.RData")
# save(topic.keys.result, topic.docs, topic.docs.norm, file="topic_model_control.RData")

# Export CSV of topic proportions in documents
topic.docs.export <- topic.docs.norm
colnames(topic.docs.export) <- short.names
write.csv(x=topic.docs.export, file="../Output/topic-docs.csv", row.names=TRUE)
# write.csv(x=topic.docs.export, file="../Output/topic-docs_control.csv", row.names=TRUE)

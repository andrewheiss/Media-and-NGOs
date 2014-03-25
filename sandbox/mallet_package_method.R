############
# This would be the best way to run MALLET, but it unfortunately doesn't let you set a seed, which is lame. 
# So instead we have to build a huge MALLET command and run it with system()
############

require(mallet)
library(ggplot2)
library(reshape2)
library(plyr)

# Set baseline variables
base.directory <- "~/Desktop/mallet_graphs"
stoplist <- "stopwords.txt"
num.topics <- 25

setwd(base.directory)



# Load documents into dataframe with three columns:
#  id: the filename with the full path stripped
#  text: the text of the article
#  publication: the name of the publication, extracted from the id

documents <- mallet.read.dir("/Users/andrew/Dropbox/Media and NGOs in the ME/Mallet/mallet_input/")
documents$id <- basename(documents$id)  # Strip path
documents$publication <- regmatches(documents$id, regexpr("^[^_]+", documents$id))  # Extract 'ahram' from 'ahram_11091.txt'

# Create a Mallet instance list from documents
mallet.instances <- mallet.import(documents$id, documents$text, stoplist, token.regexp = "\\p{L}[\\p{L}\\p{P}]+\\p{L}")

# Create initial topic trainer object
set.seed(12345)
topic.model <- MalletLDA(num.topics)
# This doesn't work, but should. RTopicModel.java is a wrapper for ParallelTopicModel, but it unfortunately doesn't have any functions for setting random seeds. If I knew Java at all, I'd patch it, but I have no clue how to add it. 
# See http://hg-iesl.cs.umass.edu/hg/mallet/file/9706cd09adb3/src/cc/mallet/topics/RTopicModel.java
# topic.model$randomSeed(1234)

# Load documents in instance list into the trainer object
topic.model$loadDocuments(mallet.instances)

## Get the vocabulary, and some statistics about word frequencies.
##  These may be useful in further curating the stopword list.
vocabulary <- topic.model$getVocabulary()
word.freqs <- mallet.word.freqs(topic.model)

# Optimize hyperparameters every 20 iterations, after 50 burn-in iterations
topic.model$setAlphaOptimization(20, 50)

# Learn the topics and train the model over 200 iterations
topic.model$train(400)

## NEW: run through a few iterations where we pick the best topic for each token, 
##  rather than sampling from the posterior distribution.
topic.model$maximize(10)


# Get the probabilities/proportions of topics in each article
doc.topics <- mallet.doc.topics(topic.model, smoothed=T, normalized=T)
# Rows = topic, columns = word in topic
topic.words <- mallet.topic.words(topic.model, smoothed=T, normalized=T)



## Get a vector containing short names for the topics
topics.labels <- rep("", num.topics)
for (topic in 1:num.topics) topics.labels[topic] <- paste(mallet.top.words(topic.model, topic.words[topic,], num.top.words=10)$words, collapse=" ")
# have a look at keywords for each topic
topics.labels

plot(hclust(dist(t(topic.docs))))
plot(hclust(dist(topic.words)), labels=topics.labels)
library(ggdendro)
HCD1 <- hclust(dist(topic.words), method="single", members=NULL)
HCD1Data <- dendro_data(as.dendrogram(HCD1))

p1 <- ggplot(data = HCD1Data$segments) +
  geom_segment(aes(x=x, y=y, xend=xend, yend=yend))
p1


# Transpose and normalize the doc topics
topic.docs.norm <- t(doc.topics)
topic.docs.norm <- topic.docs.norm / rowSums(topic.docs.norm)

# Check topics across the three publications
topic.docs <- data.frame(topic.docs.norm)
names(topic.docs) <- documents$id

topic.docs.t <- data.frame(t(topic.docs))
# topic.docs.t <- data.frame(doc.topics)
topic.docs.t$publication <- documents$publication


topic.means.wide <- ddply(topic.docs.t, ~ publication, colwise(mean))
topic.means.long <- melt(topic.means.wide, id="publication", variable.name="topic", value.name="proportion")
p <- ggplot(topic.means.long, aes(fill=as.factor(topic), x=topic, y=proportion))
p + geom_bar(stat="identity") + coord_flip() + facet_wrap(~ publication)


difference.from.second <- function(x) {
  publication <- x$publication[which.max(x$proportion)]
  n <- length(x$proportion)
  second.max <- sort(x$proportion, partial=n-1)[n-1]
  diff.from.2nd <- max(x$proportion) - second.max
  df <- data.frame(publication, diff.from.2nd)
}

diff.means <- ddply(topic.means.long, ~ topic, difference.from.second)
p <- ggplot(diff.means, aes(x=topic, y=diff.from.2nd, fill=publication))
p + geom_bar(stat="identity") + coord_flip()

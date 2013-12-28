# Title:          plot_topic_model.R
# Description:    Plot the proportions of topics in the topic model
# Author:         Andrew Heiss
# Last updated:   2013-12-28
# R version:      ≥3.0

# Load libraries
library(ggplot2)
library(grid)
library(scales)
library(plyr)
library(reshape2)

# Load topic model
load("topic_model.RData")

# Add publication name
topic.docs.norm$publication <- factor(regmatches(row.names(topic.docs.norm), regexpr("^[^_]+", row.names(topic.docs.norm))), 
                                      labels=c("Al-Ahram English", "Daily News Egypt", "Egypt Independent"))

# Calculate means and standard deviations of normalized proportions
topic.means.wide <- ddply(topic.docs.norm, ~ publication, colwise(mean))  # TODO: colwise custom function that returns mean and sd?
topic.means.long <- melt(topic.means.wide, id="publication", variable.name="topic", value.name="proportion")
topic.means.long$label <- factor(topic.means.long$topic, labels=topic.keys.result$short.names)

topic.sds.wide <- ddply(topic.docs.norm, ~ publication, colwise(sd))
topic.sds.long <- melt(topic.sds.wide, id="publication", variable.name="topic", value.name="stdev")
topic.means.long$stdev <- topic.sds.long$stdev

#-------------
# Plot stuff
#-------------
# TODO: Add confidence intervals?
# Calculate the distance between the highest and second-highest 
# proportions between publications. So if topic 1 is .4 in ahram, 
# .5 in egind, and .8 in dne, this function would return .3
difference.from.second <- function(x) {
  publication <- x$publication[which.max(x$proportion)]
  n <- length(x$proportion)
  second.max <- sort(x$proportion, partial=n-1)[n-1]
  diff.from.2nd <- max(x$proportion) - second.max
  df <- data.frame(publication, diff.from.2nd)
}

# Add spaces after legend titles to help with spacing
topic.means.long$publication <- paste(topic.means.long$publication, "   ")  

# Bar plot of absolute proportions
p <- ggplot(topic.means.long, aes(x=label, y=proportion))
p + geom_bar(stat="identity") + facet_wrap(~ publication) + 
  scale_y_continuous(labels=percent) + coord_flip() + 
  labs(x=NULL, y=NULL) + 
  theme_bw()
#   geom_errorbar(aes(ymin=proportion-stdev, ymax=proportion+stdev))

# Bar plot of distance from #1 and #2
diff.means <- ddply(topic.means.long, ~ label, difference.from.second)
p <- ggplot(diff.means, aes(x=label, y=diff.from.2nd, fill=publication))
p + geom_bar(stat="identity") + 
  scale_y_continuous(labels=percent) + coord_flip() + 
  scale_fill_brewer(palette="Set1", name="") + 
  labs(x=NULL, y=NULL) + 
  theme_bw() + theme(legend.position="bottom", legend.key.size = unit(.7, "line"))

# Bar plot and jittered points of absolute proportions
plot.data <- melt(data=topic.docs.norm, id.vars="publication")  # Use full data instead of generated means
plot.data$label <- factor(plot.data$variable, labels=topic.keys.result$short.names)
p <- ggplot(data=plot.data, aes(x=label, y=value))

# Just jittering
p + geom_point(position="jitter", alpha=0.4) + coord_flip() + facet_wrap(~ publication) + theme_bw()

# Jittering + bar plot
p + stat_summary(aes(group=1), fun.y=mean, geom="bar") + 
  geom_point(position="jitter", alpha=0.4) + coord_flip() + facet_wrap(~ publication) + theme_bw()

# Violin plots (really hard to read)
# p + geom_violin(size=0.25) +
#   stat_summary(aes(group=1), fun.y=mean, geom="point") + 
#   coord_flip() + facet_wrap(~ publication) + labs(x=NULL, y=NULL)

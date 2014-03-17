# Title:          plot_topic_model.R
# Description:    Plot the proportions of topics in the topic model
# Author:         Andrew Heiss
# Last updated:   2013-12-28
# R version:      ≥3.0

# Inspiration from Ben Marwick's Day of Archaeology example: 
# https://github.com/benmarwick/dayofarchaeology

# MAYBE: Fine tune the model with this: http://www.matthewjockers.net/2013/04/12/secret-recipe-for-topic-modeling-themes/

# Load libraries
library(ggplot2)
library(grid)
library(scales)
library(plyr)
library(reshape2)

# Load topic model
load("topic_model.RData")
# load("topic_model_control.RData")

# Add publication name
topic.docs.norm$publication <- factor(regmatches(row.names(topic.docs.norm), regexpr("^[^_]+", row.names(topic.docs.norm))), 
                                      labels=c("Al-Ahram English", "Daily News Egypt", "Egypt Independent"), ordered=TRUE)

# Calculate means and standard deviations of normalized proportions
topic.means.wide <- ddply(topic.docs.norm, ~ publication, colwise(mean))  # TODO: colwise custom function that returns mean and sd?
topic.means.long <- melt(topic.means.wide, id="publication", variable.name="topic", value.name="proportion")
topic.means.long$label <- factor(topic.means.long$topic, labels=topic.keys.result$short.names)

# topic.sds.wide <- ddply(topic.docs.norm, ~ publication, colwise(sd))
# topic.sds.long <- melt(topic.sds.wide, id="publication", variable.name="topic", value.name="stdev")
# topic.means.long$stdev <- topic.sds.long$stdev

# Get reverse topic order for correct plotting
topic.order <- topic.keys.result[order(topic.keys.result$dirichlet, decreasing=FALSE), "short.names"]
topic.means.long$label <- factor(topic.means.long$label, levels=topic.order, ordered=TRUE)

#-------------
# Plot stuff
#-------------
# Sort by Al-Ahram's proportions
resorted <- topic.means.long[with(topic.means.long, order(publication, proportion)), ]
resorted <- resorted[resorted$publication == "Al-Ahram English",]

# Merge dirichlet values into the plot data
dirichlet <- topic.keys.result
dirichlet$short.names <- factor(dirichlet$short.names, levels=resorted$label, ordered=TRUE)
dirichlet <- dirichlet[with(dirichlet, order(short.names)),]

plot.data <- topic.means.long
plot.data$label <- factor(plot.data$label, levels=resorted$label, ordered=TRUE)
plot.data <- plot.data[with(plot.data, order(label)),]
plot.data$dirichlet <- rep(dirichlet$dirichlet, each=3)

plot.data$label <- factor(plot.data$label, levels=rev(resorted$label), ordered=TRUE)

plot.data <- plot.data[plot.data$topic != "X19",]  # Remove catch-all topic
# plot.data <- plot.data[plot.data$topic != "X5",]  # Remove catch-all topic for CONTROL GROUP

# Fix stacked points
# plot.data[plot.data$topic=="X18" & plot.data$publication=="Egypt Independent",]$proportion <- 
#   plot.data[plot.data$topic=="X18" & plot.data$publication=="Egypt Independent",]$proportion + 0.00009

p <- ggplot(plot.data, aes(x=label, y=proportion, group=publication, colour=publication))
model.summary <- p + geom_point(aes(size=dirichlet), alpha=0.9, position=position_jitter(width=0, height=.00002)) + 
  scale_y_continuous(labels=percent) + coord_flip() + 
  #labs(x=NULL, y="Normalized mean of topic appearance") + theme_bw(8) + 
  labs(x=NULL, y=NULL) + theme_bw(8) + 
  theme(panel.grid.major.y=element_line(size=.6), legend.title.align=0,
        axis.ticks.y=element_blank(), legend.key = element_blank(), 
        legend.position="bottom", legend.direction = "horizontal", legend.box="horizontal", 
        legend.key.size = unit(.7, "line"), #legend.margin=unit(-.5, "line"), 
        legend.text=element_text(size=4), legend.title=element_text(size=4)) +
  scale_colour_manual(values=c("#e41a1c", "#377eb8", "#e6ab02"), name="") + 
  scale_size_continuous(range = c(1, 5), name=expression(paste("Proportion in corpus (", alpha, ")")))
model.summary

ggsave(plot=model.summary, filename="../Output/plot_topic_model_summary.pdf", width=5.5, height=4, units="in")
# ggsave(plot=model.summary, filename="../Output/plot_topic_model_summary_control.pdf", width=5.5, height=4, units="in")

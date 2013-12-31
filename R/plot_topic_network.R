# Title:          plot_topic_network.R
# Description:    Plot an arcplot and dendrogram of the topic model
# Author:         Andrew Heiss
# Last updated:   2013-12-28
# R version:      ≥3.0

# Huge thanks to Rolf Fredheim for creating the arcplot + dendrogram + topic proportions idea!
# http://quantifyingmemory.blogspot.com/2013/11/visualising-structure-in-topic-models.html

# Inspiration and help for this:
#   * http://gastonsanchez.wordpress.com/2013/02/02/star-wars-arc-diagram/
#   * http://tedunderwood.com/2012/11/11/visualizing-topic-models/

# Useful dendrogram resources:
#   * http://rpubs.com/gaston/dendrograms
#   * http://wheatoncollege.edu/lexomics/files/2012/08/How-to-Read-a-Dendrogram-Web-Ready.pdf


# Load libraries
library(ggplot2)
library(plyr)
library(reshape2)
library(ggdendro)
library(arcdiagram)

# Load topic model
load("topic_model.RData")


#-----------------------------------------
# Create correlation and dendrogram data
#-----------------------------------------
# Create data frames
df <- topic.docs.norm
df.publication <- df
df.publication$publication <- factor(regmatches(row.names(df), regexpr("^[^_]+", row.names(df))), 
                                     labels=c("Al-Ahram English", "Daily News Egypt", "Egypt Independent"))

# Create correlation matrix
cors <- cor(df)
rownames(cors) <- topic.keys.result$short.names
colnames(cors) <- topic.keys.result$short.names

# Create cluster object from matrix
cor.cluster <- hclust(dist(cors), "ward")
cor.dendro <- as.dendrogram(cor.cluster)  # Convert cluster to dendrogram


#-----------------
# Create arcplot
#-----------------
# Get pieces for arcplot
values <- colSums(cors)  # Sum of correlations for edge values
edges <- melt(cors)  # Convert to long
edges <- out[out[, 3] >= 0, ]  # Get rid of negative correlations
colnames(edges) <- c("Source","Target","Weight")
edgelist <- as.matrix(edges[, 1:2])  # Create edgelist

# Replicate the dendrogram order
arcs.order <- order.dendrogram(cor.dendro)

# Plot the arcplot
pdf(file="../Output/arcs.pdf", width=3, height=5)
arcplot(edgelist, lwd.arcs=20 * edges[,3], 
        show.nodes=TRUE, sorted=TRUE, ordering=arcs.order, 
        col.labels="red", col.arcs="#ff7f00", horizontal=FALSE)
dev.off()
# Bonus!
# This will rotate the graph by 180°, but it doesn't work in RStudio, and it can't flip the graph.
# So we need to use Photoshop to get the arcs and dendrogram to align
# library(grid)
# cap <- grid.cap()
# grid.newpage()
# grid.raster(cap, vp=viewport(angle=180))


#----------------------------------------
# Plot dendrogram and topic proportions
#----------------------------------------
# Scaling and normalizing functions
# Scale the data between exactly 0 and 1
scale.data <- function(X) {
  (X - min(X)) / diff(range(X))
}

# Square root of the column sums
sqrt.sum <- function(x) {
  sqrt(sum(x))
}

# Reorder topics to match the dendrogram
topic.order <- order.dendrogram(cor.dendro)  # Get order of dendrogram
column.names <- colnames(df)  # Get column names from publication-free data frame
topic.order <- column.names[topic.order]  # Get correct column order

# Create data frame for manually plotting the dendrogram
dendro <- ggdendro:::dendrogram_data(cor.dendro)  # Extract ggplot data frame from dendrogram object
dendro$segments$yend[dendro$segments$yend < 0.8] <- 0.8  # Cut ends of leaves off to make room for bar charts

# Create data frame for plotting different proprotions
# Proportion means
topic.means.wide <- ddply(df.publication, ~ publication, colwise(mean))
topic.means.long <- melt(topic.means.wide, id="publication", variable.name="topic", value.name="mean.prop")

# Square root of column sums
topic.sqrt.wide <- ddply(df.publication, ~ publication, colwise(sqrt.sum))
topic.sqrt.long <- melt(topic.sqrt.wide, id="publication", variable.name="topic", value.name="sqrt.sum")

# Combine into one data frame
plot.data <- topic.means.long
plot.data$topic <- factor(plot.data$topic, levels=topic.order, ordered=TRUE)
plot.data$scaled0to1 <- scale.data(plot.data$mean.prop) / 2  # Scale data
plot.data$sqrt.sum <- topic.sqrt.long$sqrt.sum / 2.4

# Plot the dendrogram and bar plots
p <- ggplot() + geom_segment(data=segment(dendro), aes(x=x, y=y, xend=xend, yend=yend)) +
  theme_dendro() + coord_flip() +
  theme(axis.text.y=element_text(hjust=1, size=13)) +
  scale_x_discrete(labels=dendro$labels$label) +
  scale_fill_brewer(palette="Set1", name="") + 
#   geom_bar(data=plot.data, aes(topic, sqrt.sum, fill=publication), stat="identity", width=.5)
  geom_bar(data=plot.data, aes(topic, scaled0to1, fill=publication), stat="identity", width=.5)
ggsave(plot=p, filename="../Output/dendro.pdf", width=7, height=5, units="in")

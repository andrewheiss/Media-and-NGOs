
# http://rpubs.com/gaston/dendrograms
# http://wheatoncollege.edu/lexomics/files/2012/08/How-to-Read-a-Dendrogram-Web-Ready.pdf

# Load topic model
load("topic_model.RData")

# Add publication name
topic.docs.norm$publication <- factor(regmatches(row.names(topic.docs.norm), regexpr("^[^_]+", row.names(topic.docs.norm))), 
                                      labels=c("Al-Ahram English", "Daily News Egypt", "Egypt Independent"))

# Create edge list for arcplot
library(ggplot2)
library(plyr)
library(reshape2)
library(ggdendro)
library(arcdiagram)

# Create correlation matrix
df <- topic.docs.norm[,-which(names(topic.docs.norm) == "publication")]  # No publication data 
cors <- cor(df)
rownames(cors) <- topic.keys.result$V3
colnames(cors) <- topic.keys.result$V3

# Create cluster object from matrix
hc <- hclust(dist(cors), "ward")
plot(hc)
hc$order
# Convert cluster to dendrogram
hc2 <- as.dendrogram(hc)
order.dendrogram(hc2)
ggdendrogram(hc2, rotate=TRUE, theme_dendro=FALSE)

# Get pieces for arcplot
values <- colSums(cors)  # Sum of correlations for edge values
out <- melt(cors)  # Convert to long
out <- out[out[,3] >= 0, ]  # Get rid of negative correlations
edgelist <- as.matrix(out[,1:2])  # Create edgelist

# Plot with the width of the arcs proportional to the values
arcplot(edgelist, lwd.arcs=20 * out[,3], show.nodes=TRUE, show.labels=FALSE, ordering=hc$order)

# Get pie graph bands
bands <- ddply(topic.docs.norm, ~ publication, function(x) sqrt(colSums(x[,-which(names(x) == "publication")])))
rownames(bands) <- bands[,1]  # Set publication names as row names
bands[,1] <- NULL  # Remove publication column
bands <- t(bands)  # Convert to long
bands

col.bands <- c("#E41A1C", "#377EB8", "#12345D")
arcBandBars(edgelist, bands,
            col.bands=col.bands, lwd=out[,3]*40, col=cols,
            col.terms="white", mar=c(1,1,3,1))

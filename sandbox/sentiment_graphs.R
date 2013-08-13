library(ggplot2)
library(reshape2)

ahram_sentiment$publication <- "ahram"
dne_sentiment$publication <- "dne"
egind_sentiment$publication <- "egind"

plot.data <- data.frame(rbind(ahram_sentiment, dne_sentiment, egind_sentiment))
plot.data$publication <- factor(plot.data$publication)
plot.data <- melt(plot.data, id=c("id_article", "publication"))

p <- ggplot(plot.data, aes(x=value, fill=publication))
p + geom_density(alpha=.7) + facet_grid(. ~ variable)

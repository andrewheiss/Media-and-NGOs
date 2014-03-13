# Title:          graphs.R
# Description:    Make pretty graphs
# Author:         Andrew Heiss
# Last updated:   2014-03-13
# R version:      ≥3.0

# Load packages
library(ggplot2)
library(grid)
library(plyr)
library(scales)
library(lubridate)

# Set working directory
base.directory <- "~/Dropbox/Media and NGOs in the ME/Media and NGOs/R"
setwd(base.directory)

# Load corpus
load("media_data.RData")

# Percent mentioning NGOs
egind.prop <- nrow(egind.ngos) / nrow(egind.articles)
ahram.prop <- nrow(ahram.ngos) / nrow(ahram.articles)
dne.prop <- nrow(dne.ngos) / nrow(dne.articles)

# NGO mentions over time
egind.monthly <- ddply(egind.articles, "month", summarise, x=length(month))
ahram.monthly <- ddply(ahram.articles, "month", summarise, x=length(month))
dne.monthly <- ddply(dne.articles, "month", summarise, x=length(month))

egind.ngos.monthly <- ddply(egind.ngos, "month", summarise, x=length(month))
ahram.ngos.monthly <- ddply(ahram.ngos, "month", summarise, x=length(month))
dne.ngos.monthly <- ddply(dne.ngos, "month", summarise, x=length(month))


merge.counts <- function(full.data, ngo.data, publication) {
  # Merge full and NGO count data frames
  merged <- merge(full.data, ngo.data, by="month")
  colnames(merged) <- c("month", "articles", "ngo.mentions")
  
  # Check for months where no NGOs are mentioned
  # Reconvert date (since doing anything to it coerces it to numeric epoch time)
  # See http://stackoverflow.com/questions/6434663/looping-over-a-date-object-result-in-a-numeric-iterator
  missing.months <- as.POSIXct(setdiff(full.data$month, ngo.data$month), origin="1970-01-01", tz="EET")
  missing.months <- floor_date(missing.months, "month")
  
  # If there are are missing months, deal with them
  if(length(missing.months) > 0) {
    # Get the full count for the missing months
    missing.article.counts <- full.data[which(full.data$month %in% missing.months),]$x
    
    # Make a partial data frame and combine with the merged one
    missing.rows <- data.frame(month=missing.months, articles=missing.article.counts, ngo.mentions=0)
    combined.monthly <- rbind(merged, missing.rows)
  } else {
    combined.monthly <- merged
  }
    
  # Calculate the proportion of NGO articles
  combined.monthly$prop <- combined.monthly$ngo.mentions / combined.monthly$articles
  
  # Add publication name
  combined.monthly$publication <- publication
  
  # Sort, just for fun
  combined.monthly <- combined.monthly[order(combined.monthly$month),]
  
  # Clear messed up row names
  row.names(combined.monthly) <- NULL

  return(combined.monthly)
}

egind.combined.monthly <- merge.counts(egind.monthly, egind.ngos.monthly, "Egypt Independent")
ahram.combined.monthly <- merge.counts(ahram.monthly, ahram.ngos.monthly, "Al-Ahram English")
dne.combined.monthly <- merge.counts(dne.monthly, dne.ngos.monthly, "Daily News Egypt")

plot.data <- rbind(egind.combined.monthly, ahram.combined.monthly, dne.combined.monthly)
plot.data$publication <- paste(plot.data$publication, "   ")  # Add spaces after legend titles to help with spacing

p <- ggplot(aes(x=month, y=prop, colour=publication), data=plot.data)
p <- p + geom_line(size=1) + 
  scale_y_continuous(labels=percent) + labs(x=NULL, y=NULL) + 
  scale_colour_brewer(palette="Set1", name="") + 
  theme_bw(10) + theme(legend.position="bottom", legend.key.size = unit(.7, "line"), legend.key = element_blank())

ggsave(plot=p, filename="../Output/figure_2.pdf", width=5.5, height=4, units="in")

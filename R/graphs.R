# Title:          graphs.R
# Description:    Make pretty graphs
# Author:         Andrew Heiss
# Last updated:   2013-08-13
# R version:      ≥3.0

# Load packages
library(ggplot2)
library(plyr)
library(stringr)
library(lubridate)

# Load data
load("~/Research/Datasets/media_data.RData")

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
  
  # Reconvert date (since doing anything to it coerces it to numeric epoch time)
  # See http://stackoverflow.com/questions/6434663/looping-over-a-date-object-result-in-a-numeric-iterator
  missing.months <- as.POSIXct(setdiff(full.data$month, ngo.data$month), origin="1970-01-01", tz="EET")
  missing.months <- floor_date(missing.months, "month")
  
  # Get the full count for the missing months
  missing.article.counts <- full.data[which(full.data$month %in% missing.months),]$x
  
  # Make a partial data frame and combine with the merged one
  missing.rows <- data.frame(month=missing.months, articles=missing.article.counts, ngo.mentions=0)
  combined.monthly <- rbind(merged, missing.rows)
  
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

p <- ggplot(aes(x=month, y=prop, fill=publication), data=plot.data)
p + geom_bar(stat="identity", position="dodge") + coord_cartesian(ylim = c(0, .15))
#############################################################################################
# Filename: Full_metabolism_Sankey.R
#
# Author: Fabian Schipfer (FS)
# Created: 14-June-2021
#
# Version: 1.2
#
# Changed on: 
#         preparation for outsourcing 
# Run on: RStudio Version 1.4.1103 with R version 4.0.2 (64-Bit)
#############################################################################################
#
#
#
# Data files required:   EU28metabolism_2017_mass2021-01-27.rds
# Subfunctions:          none
# R-files required:      none
# other files:           none
# Problems:              none
#############################################################################################
#
# Requests for optimizing the illustration
#   (1) translation into some more flexible language for online presentation and integration into the IEA Bioenergy Homepage  
#   (2) Grid in the background with column headers: c(source, availability, processing, servies/good, output) and row headers c(Food flows, energy flows, material flows)
#   (3) fixed vertical alignment as illustrated in the additional document
#   (4) Units in the hovering text (kt)
#   (X) Additional requests could include
#         (X.1) updated database without changes in the structure
#         (X.2) or also additional flows/nodes
#         (X.3) hoovering text getting the ability to klick and expand information text box
#
#
#
#
#############################################################################################

rm(list = ls())
setwd("~/IEATask40V/Bioeconomy/Fromdesktop")
library(plotly)
library(gplots)
sk <- readRDS("EU28metabolism_2017_mass2021-01-27.rds")

######## Step x: produce Sankey
labelnames <- unique(c(unique(sk$Source),unique(sk$Target)))
labelpositions <- labelnames
Nodelevels <- c("Sourcing","Availability","Processing","Services","Back-outflows")
for(i in 1:length(unique(sk$Source))){
  labelpositions[i] <- sk[sk$Source == labelnames[i],][1,]$Source.level
}
for(i in (length(unique(sk$Source))+1):length(labelnames)){
  labelpositions[i] <- sk[sk$Target == labelnames[i],][1,]$Target.level
}
mylist <- list(c(0),c(0),c(0),c(0),c(0))
ypos <- labelnames
for(i in 1:length(Nodelevels)){
  for(j in 1:length(which(match(labelpositions,Nodelevels)==i))){
    if(j == 1) mylist[[i]][j] <- 1/length(which(match(labelpositions,Nodelevels)==i)) else
      mylist[[i]][j] <- mylist[[i]][j-1] + 1/length(which(match(labelpositions,Nodelevels)==i))
    #ypos[which(match(labelpositions,Nodelevels)==i)[j]] <- sum(sk[sk$Source==labelnames[which(match(labelpositions,Nodelevels)==i)][j],]$Value,na.rm=TRUE)/sum(sk[sk$Source.level==Nodelevels[i],]$Value,na.rm=TRUE)
  }
}
#mylist2 <- list(c(0.3,0.6,1),c(0.3,0.6,1)+.2,c(0.8,1,0.2,0.5,0.6,0.7)-.3,c(0.3,0.4,1,0.6,0.7,0.9,0.1)-.3,c(1,0.6,0.3))
fig <- plot_ly(
  #data = sk, #%>% filter(Year < 2020),
  type = "sankey",
  arrangement= "snap",
  #domain = list(
  #x =  c(0,1),
  #y =  c(0,1)
  #),
  #orientation = "h",
  #valueformat = ".0f",
  #valuesuffix = "TJ",
  node = list(
    label = labelnames,
    color = "cornsilk",
    x = match(labelpositions,Nodelevels)/5-.2,
    #y = c(rep(NA,length(labelnames))), seems to NA all x value too
    y = unlist(mylist), #unweighted - x & y has to be fixed
    pad = 5,
    thickness = 5),
  #line = list(
  #color = "black",
  #width = 0.5
  #),
  #groups = list(which(match(labelpositions,Nodelevels)==1),which(match(labelpositions,Nodelevels)==2),which(match(labelpositions,Nodelevels)==3),which(match(labelpositions,Nodelevels)==4),which(match(labelpositions,Nodelevels)==5))
  link = list(
    source = match(sk$Source,labelnames)-1,
    target = match(sk$Target,labelnames)-1,
    value =  as.integer(sk$Value)/1000,
    label =  sk$Label,
    color = paste(col2hex(sk$Colour),66,sep="")
  )
)%>% 
  layout(
    title = "EU28 material flows in 2017 [kt] Source | Availability | Processing | Services/goods | Out-backflows </a>",
    font = list(
      size = 10
    )#,
    #xaxis = list(showgrid = F, zeroline = F),
    #yaxis = list(showgrid = F, zeroline = F)
  )
fig


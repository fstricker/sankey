setwd("C:/Users/schipfer/Desktop")
#install.packages("readxl")
#install.packages("plotly")
library("readxl")
library(plotly)
library(data.table)
library(magrittr)
#library(crosstalk)
library(leaflet)

ss <- read_excel("Origin_v1.xlsx",sheet = 1)


df <- ss %>% select(Source,Target,Label,Mass_2017,Value_2017,Energy_2017,Carbon_2017, Datasource,Linkfarbe)
df$Year <- rep(2017,dim(df)[1])
setnames(df, old = c("Mass_2017", "Value_2017","Energy_2017","Carbon_2017"),new = c("Mass", "Value","Energy","Carbon"))

dfm <- ss %>% select(Source,Target,Label,Mass_medium,Value_medium,Energy_medium,Carbon_medium, Datasource,Linkfarbe)
dfm$Year <- rep(2030,dim(dfm)[1])
setnames(dfm, old = c("Mass_medium", "Value_medium","Energy_medium","Carbon_medium"),new = c("Mass", "Value","Energy","Carbon"))

dfl <- ss %>% select(Source,Target,Label,Mass_long,Value_long,Energy_long,Carbon_long, Datasource,Linkfarbe)
dfl$Year <- rep(2050,dim(dfl)[1])
setnames(dfl, old = c("Mass_long", "Value_long","Energy_long","Carbon_long"),new = c("Mass", "Value","Energy","Carbon"))

df[c(4,5,6,7)] <- sapply(df[c(4,5,6,7)],as.integer)/1000
dfm[c(4,5,6,7)] <- sapply(dfm[c(4,5,6,7)],as.integer)/1000
dfl[c(4,5,6,7)] <- sapply(dfl[c(4,5,6,7)],as.integer)/1000

df <-rbind(df,dfm,dfl)
#dim(df %>% filter(Year == 2017))
#df <- ss
#df <- highlight_key(df)

fig <- plot_ly(
  data = df %>% filter(Year < 2020),
  type = "sankey",
  domain = list(
    x =  c(0,1),
    y =  c(0,1)
  ),
  orientation = "h",
  valueformat = ".0f",
  valuesuffix = "Mt",
  node = list(
    label = c(unique(df$Source),unique(df$Target)),
    color = "cornsilk",
    pad = 15,
    thickness = 15,
    line = list(
      color = "black",
      width = 0.5
    )
  ),
  
  link = list(
    source = match(df$Source,c(unique(df$Source),unique(df$Target)))-1,
    target = match(df$Target,c(unique(df$Source),unique(df$Target)))-1,
    value =  ~Mass,
    label =  df$Label,
    color = df$Linkfarbe
  )
)
fig <- fig %>% add_trace(
  #inherit = FALSE,
  #fig,
  visible = FALSE,
  data = df %>% filter(Year == 2030),
  type = "sankey",
  domain = list(
    x =  c(0,1),
    y =  c(0,1)
  ),
  orientation = "h",
  valueformat = ".0f",
  valuesuffix = "Mt",
  node = list(
    label = c(unique(dfm$Source),unique(dfm$Target)),
    #color = scolors,
    pad = 15,
    thickness = 15,
    line = list(
      color = "black",
      width = 0.5
    )
  ),
  
  link = list(
    source = match(dfm$Source,c(unique(dfm$Source),unique(dfm$Target)))-1,
    target = match(dfm$Target,c(unique(dfm$Source),unique(dfm$Target)))-1,
    value = ~Mass,
    label = dfm$Label,
    color = dfm$Linkfarbe
  )
)
fig <- fig %>% add_trace(
  #inherit = FALSE,
  #fig,
  visible = FALSE,
  data = df %>% filter(Year == 2050),
  type = "sankey",
  domain = list(
    x =  c(0,1),
    y =  c(0,1)
  ),
  orientation = "h",
  valueformat = ".0f",
  valuesuffix = "Mt",
  node = list(
    label = c(unique(dfl$Source),unique(dfl$Target)),
    #color = scolors,
    pad = 15,
    thickness = 15,
    line = list(
      color = "black",
      width = 0.5
    )
  ),
  
  link = list(
    source = match(dfl$Source,c(unique(dfl$Source),unique(dfm$Target)))-1,
    target = match(dfl$Target,c(unique(dfl$Source),unique(dfm$Target)))-1,
    value =  ~Mass,
    label =  dfm$Label,
    color = "green"
  )
)
fig <- fig %>% layout(
  #data = df,
  title = "EU27 material flows (dry mass values)",
  font = list(
    size = 10
  ),
  xaxis = list(showgrid = F, zeroline = F),
  yaxis = list(showgrid = F, zeroline = F),
  updatemenus = list(
    #list(
      #y = 0.6,
      #buttons = list(
        #list(method = "restyle",
             #args = list("link.value", list(~Mass)),
             #label = "Mass_total"),
        
        #list(method = "restyle",
             #args = list("link.value", list(~Carbon)),
             #label = "Mass_carbon"))),
    
    list(
      y = 0.7,
      buttons = list(
        list(method = "restyle",
             args = list("visible", c(TRUE, FALSE, FALSE)),
             label = "Current"),
        
        list(method = "restyle",
             args = list("visible", c(FALSE, TRUE, FALSE)),
             label = "Medium term"),
        
        list(method = "restyle",
             args = list("visible", c(FALSE, FALSE, TRUE)),
             label = "Long term")))
  )
)


fig

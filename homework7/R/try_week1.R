df <- read.csv('telecom_churn.csv')
head(df)

dim(df)
nrow(df)
ncol(df)
colnames(df)
str(df)

sapply(df, function(x) sum(is.na(x)))

df['Churn'] = df$Churn == "True"
str(df$Churn)

summary(df)
table(df$Churn)

prop.table(table(df$Area.code))

head(order(df$Total.day.charge, decreasing = T))
df[order(df$Total.day.charge, decreasing = T), ]

library(dplyr)
arrange(df, Churn, desc(Total.day.charge))

mean(df[, 'Churn'])
mean(df$Churn)






rm(list = ls())
################################################################################################################
################################################################################################################
setwd("C:/Users/tbndo/Google Drive/Projects/COVID-19/Exploratory data analysis")

library(odbc)
library(tidyverse)
library(lubridate)
library(janitor)
library(magrittr)
library(ggrepel)
library(viridis)
library(plotly)
library(gridExtra)
library(ggthemes)
################################################################################################################
################################################################################################################
theme_set(
  theme_economist() +
    theme(
      axis.text = element_text(size = 12),
      strip.text = element_text(size = 14),
      strip.switch.pad.grid = 
    ) 
  
)


################################################################################################################
################################################################################################################
con <- dbConnect(odbc(),
                 Driver = "SQL Server",
                 Server = "LAPTOP-D9C6NLOS\\SQLEXPRESS",
                 Database = "Covid_19",
                 UID = "sa",
                 PWD = rstudioapi::askForPassword("edsa@2020"),
                 Port = 1433, 
                 Trusted_Connection = "True")


con %>%
  tbl('Countries') %>%
  select(everything()) %>%
  tbl_df ->
  Countries

con %>%
  tbl('casesGlobal') %>%
  select(everything()) %>%
  tbl_df ->
  casesGlobal

con %>%
  tbl('testsGlobal') %>%
  select(everything()) %>%
  tbl_df ->
  testsGlobal

con %>%
  tbl('populationGlobal') %>%
  select(everything()) %>%
  tbl_df ->
  populationGlobal

################################################################################################################
################################################################################################################

Countries = read_csv('Countries.csv')
casesGlobal <- read_csv('casesGlobal.csv')
testsGlobal <- read_csv('testsGlobal.csv')
populationGlobal = read_csv('populationGlobal.csv')

################################################################################################################
################################################################################################################
Countries %>%
  left_join(
    casesGlobal
  ) %>%
  left_join(
    testsGlobal,
    by = c("date", "country_id")
  ) %>% 
  left_join(
    populationGlobal %>%
      mutate(population = as.numeric(population)),
    by = 'country_id'
  ) %>%
  mutate(date = as_date(date)) %>%
  select(date, day, country, country_id, continent, everything()) ->
  df

all_countries = df %>% '$'(country) %>% unique
daily_data <- tibble()

for (i in all_countries) {
  
  df %>%
    filter(country == i) %>% 
    fill(total_tests, .direction = c('down')) ->
    data

  data %>%
    rbind(
      daily_data
    )  %>%
    select(date, day, country, everything()) -> 
    daily_data
  
}

################################################################################################################
################################################################################################################
### We want to analyse countries that have done well interms of contasining the virus
### 1. We want slowly growing infections
### 2. We want countries high recovery rates
### We also want the opposite of these qualities

### First look at rate of growth in confirmed cases, then look at recoveries - this naturally leads 
### to the analysis of growth in active cases (cases excluding recoveries).

### select(date, Day, country, active, confirmed, recovered, active_dailiy_growth_rate, 
###         active_rolling_3_day_growth_rate, daily_change_in_active_cases)


daily_data %<>%
  mutate(
    'Infections per Million' = round((confirmed / population) * 1000000, 2),
    'Tests per Thousand' = round((total_tests / population) * 1000, 2),
    'Infections per Thousand Tested' = round((confirmed / total_tests) * 1000, 0),
    'Deaths per Thousand Confimed Cases' = round((deaths / confirmed) * 1000, 0),
    'Recoveries per Thousand Confirmed Cases' = round((recovered / confirmed) * 1000, 0) 
    ) 
  
daily_data %>% 
  group_by(country) %>%
  summarise(
    highest_transmission_rate = max(`Infections per Million`, na.rm = T),
    highest_infection_rate = max(`Infections per Thousand Tested`, na.rm = T),
    highest_confirmed= max(confirmed, na.rm = T),
    highest_death_rate = max(`Deaths per Thousand Confimed Cases`, na.rm = T),
    highest_recovery_rate = max(`Recoveries per Thousand Confirmed Cases`, na.rm = T)
  ) ->
  filter_data

################################################################################################################
################################################################################################################

plot_graph <- function(df, column, .filter) {
  
  df %>%
    select(date, day, country, column) %>%
    filter(country %in% .filter) %>%
    gather(feature, value, -c('date', 'day', 'country')) ->
    daily_data_trans
  
  daily_data_trans %>%
    group_by(country, feature) %>%
    summarise(day = max(day, na.rm = T),
              value = max(value, na.rm = T)) ->
    mask_df
  
  daily_data_trans  %>%
    ggplot(aes(day, value, color = country)) +
    geom_line() +
    facet_wrap( ~ feature, scales = 'free_y', nrow = 2, strip.position = 'left') +
    geom_point(data = mask_df) +
    geom_text_repel(aes(label = country), 
                    data = mask_df,
                    vjust = -1) +
    scale_x_continuous(breaks = seq(0, length(daily_data_trans$day %>% unique), 5)) +
    scale_y_continuous(labels = scales::comma) +
    theme(
      legend.position = 'none',
      strip.placement = 'outside'
    ) +
    labs(
      x = 'Number of days since inception', y = '',
      title = 'South Africa Vs other countries'
    ) -> 
    fig1 
  
  return(fig1)
  
  
}

################################################################################################################
################################################################################################################

filter_data %>%
  top_n(n = 20, wt = highest_confirmed) %>%
  '$'(country) %>%
  union(c('South Africa')) ->
  top_countries_by_confirmed

plot_graph(
  df = daily_data, column = 'confirmed', .filter = top_countries_by_confirmed
) 

filter_data %>% 
  top_n(n = 20, wt = highest_transmission_rate) %>%
  '$'(country) %>%
  union(c('South Africa')) ->
  top_countries_by_transmission
  
plot_graph(
  df = daily_data, column = 'Infections per Million', .filter = top_countries_by_transmission
)

################################################################################################################
################################################################################################################


filter_data %>%
  arrange(highest_infection_rate) %>% # default arranges by ascending order
  '$'(country) %>%
  .[c(1:20)] %>%
  union(c('South Africa')) ->
  bottom_countries_by_infection

plot_graph(
  df = daily_data, column = 'Infections per Million', .filter = bottom_countries_by_infection
)


################################################################################################################
################################################################################################################
current_day_sa <- daily_data %>% filter(country == 'South Africa') %>% '$'(day) %>% max()
.filter = top_countries_by_transmission

daily_data %>% 
  select(date, day, country, deaths, recovered, active) %>%
  filter(day == current_day_sa) %>%
  gather(feature, value, -c(date, day, country)) %>%
  group_by(country) %>% 
  summarise(Total = sum(value)) ->
  total_confirmed

daily_data %>% 
  select(date, day, country, deaths, recovered, active) %>%
  filter(day == current_day_sa) %>%
  gather(feature, value, -c(date, day, country)) %>%
  group_by(country) %>%
  left_join(
    total_confirmed
  ) %>%
  mutate(Percentage = round((value / Total) * 1000, 2)) %>%
  filter(country %in% .filter) ->
  perc_data 

perc_data %>%
  filter(feature == 'recovered') %>%
  arrange(Percentage) %>% 
  ungroup %>%
  mutate(order = c(1:nrow(perc_data))[1:length(.filter)]) %>%
  select(country, order) %>%
  full_join(
    perc_data
  ) ->
  perc_data

perc_data %>% 
  ggplot(aes(Percentage, order, fill = feature)) +
  geom_col() +
  scale_y_continuous(breaks = perc_data$order, labels = perc_data$country) +
  scale_x_continuous(breaks = seq(0, 1000, 200)) +
  theme(
    legend.title = element_blank()
  ) +
  labs(
    x = "Cases per Thousand Confirmed", y = ""
  )


################################################################################################################
################################################################################################################

daily_data %>%
  filter(day == current_day_sa & !is.na(total_tests)) %>%
  select(country, `Tests per Thousand`, `Infections per Thousand Tested`) %>%
  gather(feature, value, -c(country)) %>%
  arrange(feature, value) %>%
  filter(country %in% .filter) %>%
  mutate(feature = factor(feature, 
                          levels = c('Tests per Thousand', 'Infections per Thousand Tested')),
         order = row_number(),
         indicator = ifelse(country == 'South Africa', '1', '0')) ->
  perc_data


ggplotly(
  perc_data %>% 
    ggplot(aes(value, order, fill = indicator)) +
    geom_col() +
    facet_wrap( ~ feature, scales = 'free') +
    scale_y_continuous(breaks = perc_data$order, labels = perc_data$country) +
    theme(
      legend.position = 'none'
    )
  
)

################################################################################################################
################################################################################################################







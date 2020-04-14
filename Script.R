library(tidyverse)
library(magrittr)
library(ggrepel)
library(plotly)

df = read_csv("covid19_data.csv")
df 

cols = c('#8B4513', '#A0522D', '#D2691E', 
         '#CD853F', '#F4A460', '#DEB887', 
         '#D2B48C', '#BC8F8F', '#FFE4B5', 
         '#FFDAB9', '#FFE4E1', '#FAF0E6')
theme_set(
  theme_light() 
) 


df %>%
  select(Date, Day, Province, 'Cases by Province') %>%
  group_by(Province) %>%
  mutate(cumul_sum = cumsum(`Cases by Province`)) ->
  cases_by_province 


cases_by_province %>% 
  ungroup() %>%
  mutate(Province = factor(Province, 
                           levels = c('Gauteng', 'Western Cape', 'KwaZulu Natal', 'Unknown', 
                                      'Freestate', 'Mpumalanga', 'Limpopo', 'Eastern Cape', 
                                      'North West', 'Northern Cape'))) %>%
  ggplot(aes(Day, cumul_sum, color = Province)) +
  geom_point() +
  geom_line() +
  geom_text_repel(aes(label = Province), 
            data = cases_by_province %>% filter(Day == max(Day)),
            hjust = -.5, vjust = -1) +
  theme(
    legend.position = 'right'
  ) +
  labs(
    x = 'Day', y = 'Number of infections', title = 'Anatomy of COVID-19 in South African Provinces'
  ) +
  scale_x_continuous(breaks = c(-1:45), limits = c(-1, 45)) +
  scale_y_continuous(breaks = seq(0, 450, 50)) +
  scale_color_brewer(palette = "RdYlBu", direction = -1) 

ggplotly(g1)

df$`Total tested` <- ifelse(df$`Total tested` == 0, NA, df$`Total tested`)

df = fill(df, c('Total tested'), .direction = c('down'))


df %>%
  filter(Province == 'Gauteng') %>%
  select(Day, `New cases`, `Total cases`, `Total tested`) %>%
  mutate(Tested = c(`Total tested`[1], diff(`Total tested`))) %>% 
  mutate(Tested = ifelse(Tested == 0, NA, Tested),
         infection_rate = round((`New cases` / `Tested`) * 100, 2)) ->
  infection_data

infection_data %>%
  gather(key = 'feature', value = 'value', -c('Day', 'Total cases', 'Total tested')) %>%
  ggplot(aes(Day, value, color = feature)) +
  geom_point() +
  geom_line() +
  facet_wrap( ~ feature, nrow = 5, scale = 'free') +
  theme(
    legend.position = 'none'
  ) +
  scale_x_continuous(breaks = c(-1:45)) +
  scale_colour_manual(values = cols) ->
  g2

ggplotly(g2)
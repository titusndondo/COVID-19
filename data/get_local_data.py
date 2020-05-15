#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from datetime import datetime
import requests
from bs4 import BeautifulSoup


# In[17]:


class Scraper():
    
    def __init__(self, url = 'https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_South_Africa#Cases'):
        
        self.url = url
        self.request = requests.get(self.url)
        self.website = self.request.text
        
        self.soup = BeautifulSoup(self.website, features = "lxml")
        self.table = self.soup.find('table', {'class': 'wikitable'})
        
    def Extract(self):

        self.col_names = list()
        for node in range(16):
            value = ', '.join(self.table.findAll('th')[node].text.split())
            self.col_names.append(value)
            
        self.col_names.insert(11, 'New cases')
        self.col_names.insert(13, 'New deaths')

        self.columns = 18
        self.rows = len(self.table.findAll('tr'))

        self.df = pd.DataFrame(index = range(self.rows))

        for column in range(self.columns):
            values = list()
            for each_row in range(self.rows):
                row = self.table.findAll('tr')[each_row].findAll('td')
                if len(row) == self.columns:
                    value = ', '.join(row[column].text.split())
                    if ']' in value:
                        values.append(value.split(']')[1])
                    elif value == '?':
                        values.append(np.nan)
                    elif value and ']' not in value:
                        values.append(value)
                    else:
                        values.append(0)

                    self.df['{}'.format(column)] = pd.Series(values)

#         self.df.columns = self.col_names
        self.df = self.df.dropna(how = 'all')
        self.df['Day'] = range(-1, len(self.df) - 1)

        return self.df
    
    
    def Transform(self, extract):

        self.extract = extract
        self.df = self.extract
        self.df = self.df.rename(
            columns = {
                '2020': 'Date',
                'EC': 'Eastern Cape',
                'FS': 'Freestate',
                'GP': 'Gauteng',
                'KZN': 'KwaZulu Natal',
                'LP': 'Limpopo',
                'MP': 'Mpumalanga',
                'NW': 'North West',
                'NC': 'Northern Cape',
                'WC': 'Western Cape',
                'un': 'Unknown',
                'Confirmed': 'Total cases',
                'Deaths': 'Total deaths',
                'Rec': 'Recovered',
                'Agtests': 'Total tested'
            }
        )

        self.df.drop(labels = ['Ref'], axis = 1, inplace = True)

        self.df = pd.melt(
            self.df,
            id_vars = ['Date', 'Day', 'New cases', 'Total cases', 'New deaths', 'Total deaths', 'Recovered', 'Total tested'],
            var_name = 'Province',
            value_name = 'Cases by Province'
        )

        date = self.df['Date'] + '-20'
        self.df['Date'] = date.apply(lambda date: datetime.strptime(date, '%m-%d-%y'))

        self.columns = [
            'Date', 'Day', 'Province', 'Cases by Province', 'New cases', 'Total cases', 
            'Total tested', 'New deaths', 'Total deaths', 'Recovered'
        ]
        self.df = self.df.loc[:, self.columns]

        self.df = self.df.astype(
            { 
               'Province': 'category',
               'Cases by Province': 'float', 
               'New cases': 'int', 
               'Total cases': 'int', 
               'Total tested': 'int', 
               'New deaths': 'int', 
               'Total deaths': 'int', 
               'Recovered': 'int'
            }
        )

        return self.df



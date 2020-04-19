import pandas as pd
import numpy as np
from datetime import datetime
import requests
from bs4 import BeautifulSoup



def testsGlobal():
    """
    Get COVID19 Global testing data  
    Provided by: Our World in Data
    website: https://ourworldindata.org/covid-testing 
    github: https://github.com/owid/covid-19-data
    
    Usage: 
    
    import get_data
    get_data.testsGlobal()
    
    """
    
    url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
    df = pd.read_csv(url, error_bad_lines=False, index_col = 'date', parse_dates = True)
    
    tests_columns = [
        'location', 'total_tests', 'new_tests', 'total_tests_per_thousand', 'new_tests_per_thousand', 'tests_units'
    ]
    
    return df[tests_columns]


def populationGlobal():
    
    url = 'https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population'
    request = requests.get(url)
    website = request.text

    soup = BeautifulSoup(website, features = "lxml")
    table = soup.find('table', {'class': 'wikitable'})

    col_names = list()
    for node in range(6):
        col_names.append(', '.join(table.findAll('th')[node].text.split()))
    col_names

    columns = 6
    rows = len(table.findAll('tr'))

    df = pd.DataFrame(index = range(rows))

    for column in range(columns):
        values = list()
        for each_row in range(rows):
            row = table.findAll('tr')[each_row].findAll('td')
            if len(row) == 6:
                value = ', '.join(row[column].text.split('[')[0].split())
                value = value.replace(',', '')
                values.append(value)
               
                df['{}'.format(column)] = pd.Series(values)
    df.columns = col_names
    return df
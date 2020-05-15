import pandas as pd
import numpy as np
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def exploreTables():

    casesGlobal = 'https://9gnht4xyvf.execute-api.eu-west-1.amazonaws.com/api/get_table/CasesGlobalView'
    counterMeasures = 'https://9gnht4xyvf.execute-api.eu-west-1.amazonaws.com/api/get_table/CounterMeasureView'

    casesLocal = 'https://9gnht4xyvf.execute-api.eu-west-1.amazonaws.com/api/get_table/CasesLocalView'
    testsLocal = 'https://9gnht4xyvf.execute-api.eu-west-1.amazonaws.com/api/get_table/Testing'
    
    
    urls = {
        'casesGlobal': casesGlobal,
        'counterMeasures': counterMeasures,
        'casesLocal': casesLocal,
        'testsLocal': testsLocal
    }

    headers = {
        'x-api-key': "WVllUkRA01awNNgKxGg607vl5qIvuOAN3pW9HXmD"
        }

    tables = {}
    for table_name, url in urls.items():
        response = requests.request("GET", url, headers = headers)
        x = response.json()
        tables[table_name] = pd.DataFrame(x)
    
    return tables

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
    df = pd.read_csv(url, error_bad_lines=False)
    
    return df.loc[:, ['date', 'location', 'total_tests', 'new_tests']].rename(
            columns = {
                'location':'country',
                'new_tests':'tests_daily'
            }
        )

def Continents():
    url = 'https://raw.githubusercontent.com/dbouquin/IS_608/master/NanosatDB_munging/Countries-Continents.csv'
    df = pd.read_csv(url).rename(
                            columns = {
                                'Continent': 'continent',
                                'Country': 'country'
                            }
                        )
    
    return df

def populationGlobal():
    """
    Get global population data by country
    
    """
    
    url = 'https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population'
    request = requests.get(url)
    website = request.text

    soup = BeautifulSoup(website, features = "lxml")
    table = soup.find('table', {'class': 'wikitable'})

#     col_names = list()
#     for node in range(6):
#         col_names.append(', '.join(table.findAll('th')[node].text.split()))
#     col_names

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
#     df.columns = col_names
    df = df.iloc[:, [1,2]]
    df.columns = ['country', 'population']
    return df

def responsesGlobal():
    """
    Get data on Covid19 quarantines date across the globe
    
    """
    url = 'https://en.wikipedia.org/wiki/National_responses_to_the_2019%E2%80%9320_coronavirus_pandemic'
    request = requests.get(url)
    website = request.text

    soup = BeautifulSoup(website, features = "lxml")
    table = soup.find('table', {'class': 'wikitable'})
    
    col_names = list()
    node = table.findAll('tr')[1]
    for name in range(0, len(node)):
        col = node.text.split('\n')[name]
        if col:
            if col == 'Countries and territories':
                col_names.append('country')
            else:
                col_names.append(col.replace(' ', '_').lower())
    col_names.remove('place')
    
    rows = len(table.findAll('tr'))
    columns = 4

    df = pd.DataFrame(index = range(rows))
    df1 = pd.DataFrame(index = range(rows))
    df2 = pd.DataFrame(index = range(rows))

    for column in range(columns):

        values = list()
        for each_row in range(2, rows):
            row = table.findAll('tr')[each_row].findAll('td')

            if len(row) in [4]:
                value = ', '.join(row[column].text.split('[')[0].split('(')[0].split())
                value = value.replace(',', '')
                values.append(value)
                df1['{}'.format(column)] = pd.Series(values)
            elif len(row) in [5]:
                if column == 0:
                    value = ', '.join(row[column].text.split('[')[0].split())
                    value = value.replace(',', '')
                    values.append(value)
                else:
                    value = ', '.join(row[column + 1].text.split('[')[0].split())
                    value = value.replace(',', '')
                    values.append(value)

                df2['{}'.format(column)] = pd.Series(values)

                df = pd.concat([df1, df2])
    df.columns = col_names       
    return df.dropna(how = 'all')

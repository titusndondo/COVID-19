#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from dplython import select, DplyFrame, X, arrange, sift, head, summarize, group_by, tail, mutate

import pyodbc
from get_data import testsGlobal, populationGlobal, exploreTables, Continents


# In[24]:


url = 'https://raw.githubusercontent.com/Covid19R/coronavirus/master/csv/coronavirus.csv'
data = pd.read_csv(url, error_bad_lines=False)

data.rename(
    columns = {
        'Country.Region':'country',
        'Province.State':'province',
        'type':'case_type',
        'Lat':'lat',
        'Long':'long'
    }, inplace = True
)


# In[25]:


casesGlobal_temp2 = pd.pivot_table(
                            data = data,
                            index = ['date', 'country', 'province', 'lat', 'long'],
                            columns = 'case_type',
                            values = 'cases'
                        ).reset_index()
countries_w_provinces = casesGlobal_temp2['country'].unique()


# In[26]:


data.pop('province')


# In[29]:


mask = data['country'].map(lambda string: string not in countries_w_provinces)
data_copy = data[mask].copy()

mask = data['country'].map(lambda string: string in countries_w_provinces)
data_copy2 = data[mask].copy()

for country in countries_w_provinces:

    df = data_copy2[data_copy2['country'] == country].copy()
    df = df.groupby(['date', 'country', 'case_type']).sum().reset_index().sort_values('date')
    columns_order = data_copy.columns
    df = df.loc[:, columns_order]

    data_copy = pd.concat(
                    [data_copy, df]
                )
    
data_copy.max()


# In[30]:


casesGlobal_temp1 = pd.pivot_table(
                            data = data_copy,
                            index = ['date', 'country', 'lat', 'long'],
                            columns = 'case_type',
                            values = 'cases'
                        )

confirmed = casesGlobal_temp1['confirmed']
death_plus_recovered = casesGlobal_temp1['death'] + casesGlobal_temp1['recovered']

casesGlobal_temp1['active'] = confirmed.sub(death_plus_recovered)
casesGlobal_temp1.reset_index(inplace = True)
casesGlobal_temp1.max()


# In[44]:


all_countries = casesGlobal_temp1['country'].unique()

cumul_cases = pd.DataFrame(index = casesGlobal_temp1.index)

for country in all_countries:
    
    mask = casesGlobal_temp1['country'] == country
    df_copy = casesGlobal_temp1[mask].copy()
    df = df_copy[['date', 'country']].copy()

    column_names = ['confirmed', 'death', 'recovered', 'active']

    for column_name in column_names:
        df['{}'.format(column_name)] = df_copy.loc[:, column_name].cumsum()
        
    cumul_cases = pd.concat(
        [cumul_cases, df], sort = True
    )
    
cumul_cases = cumul_cases.sort_values(['date', 'country']).dropna(how = 'all')  #.iloc[:len(cumul_cases) // 2, ]
mask = pd.Series(np.where(cumul_cases['confirmed'] > 0, True, False))
cumul_cases = cumul_cases[mask]
cumul_cases


# In[45]:


def add_day(df, countriez):

    df_temp = df.copy()
    df = pd.DataFrame(index = range(0, 100000))
    
    for country in countriez:
        data = (
            DplyFrame(df_temp) >>
              sift(X.country == country)
        )

        df_filt = (
            data >>
              mutate(day = range(1, len(data) + 1)) 
        ) 

        df = pd.concat(
                    [df, df_filt], sort = False
                ).dropna(how = 'all')
        
    return df

cumul_cases = add_day(df = cumul_cases, countriez = all_countries)


# In[46]:


cumul_cases = pd.melt(
        cumul_cases,
        id_vars = ['date', 'day', 'country'],
        value_vars = ['death', 'recovered', 'active'],
        value_name = 'cum_cases',
    var_name = 'case_type'
    )


# In[47]:


daily_cases = pd.melt(
        casesGlobal_temp1,
        id_vars = ['date', 'country'],
        value_vars = ['death', 'recovered', 'active'],
        value_name = 'daily_cases'
    )


# In[48]:


casesGlobal = pd.merge(
                left = cumul_cases,
                right = daily_cases,
                how = 'left',
                on = ['date', 'country', 'case_type']
            )

casesGlobal['country'] = np.where(casesGlobal['country'] == 'Korea, South', 'South Korea', casesGlobal['country'])
casesGlobal['country'] = np.where(casesGlobal['country'] == 'US', 'United States', casesGlobal['country'])
casesGlobal['country'] = np.where(casesGlobal['country'] == 'Taiwan*', 'Taiwan', casesGlobal['country'])
casesGlobal['country'] = np.where(casesGlobal['country'] == 'Cabo Verde', 'Cape Verde', casesGlobal['country'])
casesGlobal['country'] = np.where(casesGlobal['country'] == 'Eswatini', 'Swaziland', casesGlobal['country'])


# In[49]:


from get_data import Continents

Continents = Continents()
Continents['country'] = np.where(Continents['country'] == 'Korea, South', 'South Korea', Continents['country'])
Continents['country'] = np.where(Continents['country'] == 'US', 'United States', Continents['country'])
Continents.sort_values('country', inplace = True)

Continents['country'] = np.where(Continents['country'] == 'Burkina', 'Burkina Faso', Continents['country'])
Continents['country'] = np.where(Continents['country'] == 'Burma (Myanmar)', 'Burma', Continents['country'])
Continents['country'] = np.where(Continents['country'] == 'Congo, Democratic Republic of', 'Congo (Kinshasa)', Continents['country'])
Continents['country'] = np.where(Continents['country'] == 'Congo', 'Congo (Brazzaville)', Continents['country'])
Continents['country'] = np.where(Continents['country'] == 'Korea, North', 'North Korea', Continents['country'])
Continents['country'] = np.where(Continents['country'] == 'Russian Federation', 'Russia', Continents['country'])
Continents['country'] = np.where(Continents['country'] == 'Macedonia', 'North Macedonia', Continents['country'])
Continents['country'] = np.where(Continents['country'] == 'CZ', 'Czechia', Continents['country'])
Continents['country'] = np.where(Continents['country'] == 'East Timor', 'Timor-Leste', Continents['country'])
Continents['country'] = np.where(Continents['country'] == 'Ivory Coast', "Cote d'Ivoire", Continents['country'])
Continents['country'] = np.where(Continents['country'] == 'Vatican City', "Holy See", Continents['country'])

my_dict = {
    'country': ['Taiwan', 'Kosovo', 'Diamond Princess', 'MS Zaandam', 'West Bank and Gaza', 'Western Sahara'],
    'continent':['Asia', 'Europe', 'Europe', 'Europe', 'Asia','Africa']
            
        }

more_continents = pd.DataFrame(my_dict)
Continents = pd.concat(
    [Continents, more_continents], sort = True
)


# In[50]:


countries = casesGlobal['country'].unique()
country_ids = range(1, len(countries) + 1)
Countries = pd.DataFrame(
    {
        'country': countries,
        'country_id': country_ids
    }
)

Countries = pd.merge(
    left = Countries,
    right = Continents,
    how = 'left'
)

Countries = pd.merge(
    left = Countries,
    right = casesGlobal_temp1[['country', 'lat', 'long']].drop_duplicates().groupby('country').mean().reset_index(),
    how = 'left'
)

Countries


# In[51]:


casesGlobal = pd.merge(
    left = casesGlobal,
    right = Countries,
    how = 'left'
)

columns_order = ['date', 'day', 'country_id', 'country', 'case_type', 'daily_cases', 'cum_cases']
casesGlobal = casesGlobal.loc[:, columns_order]


# In[52]:


from get_data import populationGlobal
populationGlobal = populationGlobal()


# In[53]:


populationGlobal['country'] = np.where(populationGlobal['country'] == 'DR Congo', 'Congo (Kinshasa)', populationGlobal['country'])
populationGlobal['country'] = np.where(populationGlobal['country'] == 'Congo', 'Congo (Brazzaville)', populationGlobal['country'])
populationGlobal['country'] = np.where(populationGlobal['country'] == 'Ivory Coast', "Cote d'Ivoire", populationGlobal['country'])
populationGlobal['country'] = np.where(populationGlobal['country'] == 'Czech Republic', "Czechia", populationGlobal['country'])
populationGlobal['country'] = np.where(populationGlobal['country'] == 'Eswatini', "Swaziland", populationGlobal['country'])
populationGlobal['country'] = np.where(populationGlobal['country'] == 'East Timor', "Timor-Leste", populationGlobal['country'])
populationGlobal['country'] = np.where(populationGlobal['country'] == 'São Tomé and Príncipe', "Sao Tome and Principe", populationGlobal['country'])
populationGlobal['country'] = np.where(populationGlobal['country'] == 'Vatican City', "Holy See", populationGlobal['country'])
populationGlobal['country'] = np.where(populationGlobal['country'] == 'Myanmar', "Burma", populationGlobal['country'])


my_dict = {
    'country': ['Diamond Princess', 'MS Zaandam', 'West Bank and Gaza'],
    'population':[3770, 2047, 4880000]
            
        }

more_populations = pd.DataFrame(my_dict)
populationGlobal = pd.concat(
    [populationGlobal, more_populations], sort = True
)


# In[54]:


populationGlobal = pd.merge(
    left = populationGlobal,
    right = Countries,
    how = 'right'
)

columns_order = ['country_id', 'population']
populationGlobal = populationGlobal.loc[:, columns_order]
populationGlobal


# In[55]:


from get_data import testsGlobal
testsGlobal = testsGlobal()
testsGlobal.sort_values(by = ['country', 'date'], inplace = True)

testsGlobal['country'] = np.where(testsGlobal['country'] == 'Congo', "Congo (Brazzaville)", testsGlobal['country'])
testsGlobal['country'] = np.where(testsGlobal['country'] == 'Democratic Republic of Congo', "Congo (Kinshasa)", testsGlobal['country'])
testsGlobal['country'] = np.where(testsGlobal['country'] == 'Myanmar', "Burma", testsGlobal['country'])
testsGlobal['country'] = np.where(testsGlobal['country'] == 'Czech Republic', "Czechia", testsGlobal['country'])
testsGlobal['country'] = np.where(testsGlobal['country'] == 'Vatican', "Holy See", testsGlobal['country'])
testsGlobal['country'] = np.where(testsGlobal['country'] == 'Macedonia', "North Macedonia", testsGlobal['country'])
testsGlobal['country'] = np.where(testsGlobal['country'] == 'Timor', "Timor-Leste", testsGlobal['country'])



casesGlobal = pd.merge(
    left = casesGlobal,
    right = testsGlobal,
    how = 'left'
)

columns_order = ['date', 'day', 'country_id', 'case_type', 'daily_cases', 'cum_cases', 'total_tests', 'tests_daily']
casesGlobal = casesGlobal.loc[:, columns_order]
casesGlobal


# In[56]:


casesGlobal = casesGlobal.astype(
                        {
                            'day': 'int32',
                            'country_id': 'int32'
                        }
                    )

casesGlobal.max()


# In[57]:


df_names = ['Countries', 'casesGlobal', 'populationGlobal']
dataframes = [Countries, casesGlobal, populationGlobal]
allTablesDict = {name: df for name, df in zip(df_names, dataframes)}


# In[58]:


# establish connection to local MsSQL
conn = pyodbc.connect(DRIVER='{SQL Server}',
                      SERVER='LAPTOP-D9C6NLOS\SQLEXPRESS',
                      UID ='sa', 
                      PWD = 'edsa@2020',
                      Autocommit = True
                             )    

# Return a new Cursor object using the connection.
cur = conn.cursor()

# CREATE DATABASE
cur.execute("""
            DROP DATABASE Covid_19;
            
            CREATE DATABASE Covid_19;
            """)

conn.commit()


# In[59]:


# establish connection to local MsSQL and to DATABASE
conn = pyodbc.connect(DRIVER = '{SQL Server}',
                      SERVER = 'LAPTOP-D9C6NLOS\SQLEXPRESS',
                      DATABASE = 'Covid_19',
                      UID = 'sa', 
                      PWD = 'edsa@2020',
                      Autocommit = True
                             ) 


# In[60]:


# Query to create tables

countriesTableQuery = """
                        DROP TABLE IF EXISTS Countries;
                        
                        CREATE TABLE Countries(
                        country varchar(50),
                        country_id int,
                        continent varchar(50),
                        lat nvarchar(50),
                        long nvarchar(50)
                        )

                      """

casesGlobalQuery = """ 
                        DROP TABLE IF EXISTS casesGlobal;
            
                        CREATE TABLE casesGlobal(
                        date DATE,
                        day int,
                        country_id int,
                        case_type varchar(50),
                        cum_cases varchar(50),
                        daily_cases varchar(50),
                        total_tests varchar(50),
                        tests_daily varchar(50)
                                ); 
                  """

populationTableQuery = """
                        DROP TABLE IF EXISTS populationGlobal;
                        
                        CREATE TABLE populationGlobal(
                        country_id int,
                        population varchar(50)
                        )
                       """

createTableQuiries = [countriesTableQuery, casesGlobalQuery, populationTableQuery]


# In[61]:


# Return a new Cursor object using the connection.
cur = conn.cursor()

for query in createTableQuiries:
    # run query
    cur.execute(query)
    conn.commit()


# In[62]:


for table_name, df in allTablesDict.items():

    # Return a new Cursor object using the connection.
    cur = conn.cursor()

    number_of_columns = len(df.columns)
    table_columns = str(tuple(df.columns)).replace("'", '')

    for index in df.index:
        Series = df.loc[index]

        row = list()
        for value in Series:
            value = str(value)
            if value != 'nan':
                row.append(str(value))
            else:
                row.append('NULL')

        cur.execute(
            "INSERT INTO {}{} values ({})".format(
                table_name,
                table_columns,
                ('?, ' * number_of_columns)[0:-2]
            ),
            row
    )


# In[63]:


for table_name, df in allTablesDict.items():
    cols_w_nan = df.columns[df.isna().any()].tolist()
    for column in cols_w_nan:
        
        cur.execute("UPDATE {} SET {} = NULL WHERE {} = 'NULL';".format(table_name, column, column))
        conn.commit()
        
        
        if column not in ['Country', 'country_id', 'continent']:
            cur.execute("ALTER TABLE {} ALTER COLUMN {} float;".format(table_name, column))
            conn.commit()


# In[64]:


conn.close()


# In[ ]:





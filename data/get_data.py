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

    import pandas as pd
    url = 'https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv'
    df = pd.read_csv(url, error_bad_lines=False, index_col = 'date', parse_dates = True)
    
    tests_columns = [
        'location', 'total_tests', 'new_tests', 'total_tests_per_thousand', 'new_tests_per_thousand', 'tests_units'
    ]
    
    return df[tests_columns]

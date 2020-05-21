import datetime
import os
import sys

import numpy as np
import pandas as pd


def get_iso_by_country_name(country_name, mode):
    array_iso = np.array(['BO-B',
                          'BO-H',
                          'BO-C',
                          'BO-L',
                          'BO-O',
                          'BO-N',
                          'BO-P',
                          'BO-S',
                          'BO-T'])

    array_bolivia_csv = np.array(['Beni',
                                  'Chuquisaca',
                                  'Cochabamba',
                                  'La Paz',
                                  'Oruro',
                                  'Pando',
                                  'Potosí',
                                  'Santa Cruz',
                                  'Tarija'])

    array_bolivia_fixed = np.array(['Beni',
                                    'Chuquisaca',
                                    'Cochabamba',
                                    'La Paz',
                                    'Oruro',
                                    'Pando',
                                    'Potosi',
                                    'Santa Cruz',
                                    'Tarija'])

    df = pd.DataFrame({'ISO 3166-2 Code': array_iso,
                       'Remote': array_bolivia_csv, 'Local': array_bolivia_fixed})

    string_iso = ''

    if mode == 'remote':
        string_iso = df[df['Remote'].str.contains(
            country_name)]['ISO 3166-2 Code'].values[0]
    elif mode == 'local':
        string_iso = df[df['Local'].str.contains(
            country_name)]['ISO 3166-2 Code'].values[0]

    return string_iso


def generate_list_dates(path):
    # Generate dates from files existing
    date_list_csv = []
    path, dirs, files = next(os.walk(path))
    numero_archivos = len(files)
    print('There is {} files on the path and one is README. We iterate {} times...'.format(
        numero_archivos, numero_archivos-1))
    # dates
    base = (datetime.datetime.today()).date()
    numdays = numero_archivos-1
    date_list_csv = [str(base - datetime.timedelta(days=x))+str('.csv')
                     for x in range(numdays)]
    print('Adding {} dates in a list...'.format(len(date_list_csv)))
    date_list = []
    for d in date_list_csv:
        date_list.append(d[:-4])
    print("List of dates:", date_list)
    return date_list_csv, date_list


def load_and_generatecsv(list_date_list):

    today = datetime.datetime.now().strftime('%Y-%m-%d')

    path_dsrp_daily_reports = 'latam_covid_19_data/daily_reports/'
    path_bolivia_confirmed_csv = "https://github.com/mauforonda/covid19-bolivia/raw/master/confirmados.csv"
    path_bolivia_deaths_csv = "https://github.com/mauforonda/covid19-bolivia/raw/master/decesos.csv"
    path_bolivia_recoverd_csv = "https://github.com/mauforonda/covid19-bolivia/raw/master/recuperados.csv"
    # path_ecuador_recovered (NOT FOUND)
    path_dsrp = "latam_covid_19_data/templates/daily_reports.csv"
    path_csv = "utils/scripts/data_collection/data/bolivia_temporal/"

    data_bolivia_confirmed = pd.read_csv(path_bolivia_confirmed_csv)
    data_bolivia_deaths = pd.read_csv(path_bolivia_deaths_csv)
    data_bolivia_recovered = pd.read_csv(path_bolivia_recoverd_csv)

    data_dsrp = pd.read_csv(path_dsrp)

    array_dates_csv, array_dates = generate_list_dates(path_dsrp_daily_reports)

    array_bolivia_csv = np.array(['Beni',
                                  'Chuquisaca',
                                  'Cochabamba',
                                  'La Paz',
                                  'Oruro',
                                  'Pando',
                                  'Potosí',
                                  'Santa Cruz',
                                  'Tarija'])

    array_iso = np.array(['BO-B',
                          'BO-H',
                          'BO-C',
                          'BO-L',
                          'BO-O',
                          'BO-N',
                          'BO-P',
                          'BO-S',
                          'BO-T'])

    df_confirmed = data_bolivia_confirmed.set_index('Fecha').T
    df_confirmed = df_confirmed.reset_index(drop=False)
    df_confirmed['ISO 3166-2 Code'] = df_confirmed['index'].apply(
        lambda x: get_iso_by_country_name(x, 'remote'))

    df_deaths = data_bolivia_deaths.set_index('Fecha').T
    df_deaths = df_deaths.reset_index(drop=False)
    df_deaths['ISO 3166-2 Code'] = df_deaths['index'].apply(
        lambda x: get_iso_by_country_name(x, 'remote'))

    df_recovered = data_bolivia_recovered.set_index('Fecha').T
    df_recovered = df_recovered.reset_index(drop=False)
    df_recovered['ISO 3166-2 Code'] = df_recovered['index'].apply(
        lambda x: get_iso_by_country_name(x, 'remote'))

    for d in list_date_list:  # array_dates

        temp_dsrp = data_dsrp[data_dsrp['ISO 3166-2 Code']
                              .str.contains('BO-')].copy()

        temp_dsrp['Confirmed'] = 0
        temp_dsrp['Deaths'] = 0
        temp_dsrp['Recovered'] = 0

        for iso in array_iso:

            """
            CONFIRMED
            """

            df_per_iso = df_confirmed[df_confirmed['ISO 3166-2 Code'] == iso]

            if df_per_iso[d].values[0] != '':
                number_confirmed = int(float(df_per_iso[d].values[0]))
            else:
                number_confirmed = ''

            a = temp_dsrp[temp_dsrp['ISO 3166-2 Code'] == iso]
            temp_dsrp.loc[a.index.values[0], 'Confirmed'] = number_confirmed

            """
            DEATHS
            """
            df_per_iso = df_deaths[df_deaths['ISO 3166-2 Code'] == iso]

            if df_per_iso[d].values[0] != '':
                number_deaths = int(float(df_per_iso[d].values[0]))
            else:
                number_deaths = ''

            a = temp_dsrp[temp_dsrp['ISO 3166-2 Code'] == iso]
            temp_dsrp.loc[a.index.values[0], 'Deaths'] = number_deaths

            """
            RECOVERED
            """
            df_per_iso = df_recovered[df_recovered['ISO 3166-2 Code'] == iso]

            if df_per_iso[d].values[0] != '':
                number_recovered = int(float(df_per_iso[d].values[0]))
            else:
                number_recovered = ''

            a = temp_dsrp[temp_dsrp['ISO 3166-2 Code'] == iso]
            temp_dsrp.loc[a.index.values[0], 'Recovered'] = number_recovered

        print(d, end=' - ')
        # print(temp_dsrp)
        temp_dsrp = temp_dsrp.fillna('')

        temp_dsrp.to_csv(path_csv+d+'.csv', index=False)


if __name__ == "__main__":
    load_and_generatecsv(['2020-05-21', '2020-05-20', '2020-05-19', '2020-05-18', '2020-05-17', '2020-05-16', '2020-05-15', '2020-05-14',
                          '2020-05-13', '2020-05-12', '2020-05-11', '2020-05-10', '2020-05-09', '2020-05-08', '2020-05-07', '2020-05-06',
                          '2020-05-05', '2020-05-04', '2020-05-03', '2020-05-02', '2020-05-01', '2020-04-30', '2020-04-29', '2020-04-28',
                          '2020-04-27', '2020-04-26', '2020-04-25', '2020-04-24', '2020-04-23', '2020-04-22', '2020-04-21', '2020-04-20',
                          '2020-04-19', '2020-04-18', '2020-04-17', '2020-04-16', '2020-04-15', '2020-04-14', '2020-04-13', '2020-04-12',
                          '2020-04-11', '2020-04-10', '2020-04-09', '2020-04-08', '2020-04-07', '2020-04-06', '2020-04-05', '2020-04-04',
                          '2020-04-03', '2020-04-02', '2020-04-01', '2020-03-31', '2020-03-30', '2020-03-29', '2020-03-28', '2020-03-27',
                          '2020-03-26', '2020-03-25', '2020-03-24', '2020-03-23', '2020-03-22', '2020-03-21'])

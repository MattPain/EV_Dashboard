import pandas as pd
import numpy as np

class EVCPDataExtractor:

    '''
    This script downloads the EV charge point data from the Department for Transport via the below url:
    - https://www.gov.uk/government/statistics/electric-vehicle-charging-device-statistics-january-2022
    The data is then unpivoted and cleaned before being deposited into a chosen target directory.
    This script was developed for the EV Infrastructure Planning Tool.

    The source metadata can be seen below:
    - URL = 'https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1048354/electric-vehicle-charging-device-statistics-january-2022.ods
    - file type = .ods (Excel)
    - sheet names = info, EVCD_01a, EVCD_01b, EVCD_02
    - field names = LA/Region Code, Local Authority/Region Name, Total/Rapid Devices (depending on sheet), Per100KPopulation, covers Jan, Apr, Jul, Oct for every year since Oct 2019

    Data is update quarterly and can be updated by adding a new date to the dates list in the field variables below.

    Glossary:
    EVCD - Electric Vehicle Charging Devices
    LA - Local Authority
    '''


    header_names = ['LA/RegionCode', 'LA/RegionName']
    # Add when new data becomes available
    dates = ['Jan-22', 'Oct-21', 'Jul-21', 'Apr-21', 'Jan-21', 'Oct-20', 'Jul-20', 'Apr-20', 'Jan-20', 'Oct-19']
    skip_rows = 7
    skip_footer = 13
    value_name_average = 'Per100kPopulation'

    def __init__(self, source_url: str, sink_url: str, sheet_name: str, value_name: str):
        self.source_url = source_url
        self.sink_url = sink_url
        self.sheet_name = sheet_name
        self.value_name = value_name

    def clean_data(self, replace_na = True):
        total_devices_string, per_100k_string = [self.value_name, self.value_name_average]
        final_devices_list = []
        for col_name in self.dates:
            final_devices_list.append(total_devices_string + col_name)
            final_devices_list.append(per_100k_string + col_name)
        final_devices = self.header_names + final_devices_list

        df = pd.read_excel(self.source_url, sheet_name=self.sheet_name, skiprows=self.skip_rows, engine='odf',
                      skipfooter=self.skip_footer,
                      names=final_devices)

        unpivoted_df = df.melt(id_vars=self.header_names)
        unpivoted_df['Date'] = unpivoted_df['variable'].apply(lambda x: x[-6:])
        unpivoted_df['variable'] = unpivoted_df['variable'].apply(lambda x: x[:-6])

        total_devices_df = unpivoted_df.loc[unpivoted_df['variable'] == self.value_name]
        per_100k_df = unpivoted_df.loc[unpivoted_df['variable'] == self.value_name_average]

        total_devices_df.rename(mapper={'value': self.value_name}, inplace=True, axis=1)
        per_100k_df.rename(mapper={'value': self.value_name_average}, inplace=True, axis=1)

        total_devices_df.drop('variable', inplace=True, axis=1)
        per_100k_df.drop('variable', inplace=True, axis=1)

        total_devices_df[self.header_names[1]] = total_devices_df[self.header_names[1]].apply(lambda x: x.strip())
        total_devices_df[self.header_names[1]] = total_devices_df[self.header_names[1]].apply(lambda x: x.lower())
        total_devices_df[self.header_names[1]] = total_devices_df[self.header_names[1]].apply(lambda x: x.title())

        per_100k_df[self.header_names[1]] = per_100k_df[self.header_names[1]].apply(lambda x: x.strip())
        per_100k_df[self.header_names[1]] = per_100k_df[self.header_names[1]].apply(lambda x: x.lower())
        per_100k_df[self.header_names[1]] = per_100k_df[self.header_names[1]].apply(lambda x: x.title())

        if replace_na:

            total_devices_df[self.value_name].replace('-', 0, inplace=True)
            per_100k_df[self.value_name_average].replace('-', 0, inplace=True)

            total_devices_df[self.value_name].replace(np.nan, 0, inplace=True)
            per_100k_df[self.value_name_average].replace(np.nan, 0, inplace=True)

        total_devices_df[self.value_name] = total_devices_df[self.value_name].apply(lambda x: int(x))
        per_100k_df[self.value_name_average] = per_100k_df[self.value_name_average].apply(lambda x: int(x))

        return total_devices_df, per_100k_df

    def write_date(self, dataframe, dataframe_average, file_name, file_name_average):
        dataframe.to_csv(self.sink_url + '\\' + file_name, index=False)
        dataframe_average.to_csv(self.sink_url + '\\' + file_name_average, index=False)

if __name__ == '__main__':
    evcp_data_total = EVCPDataExtractor('https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1048354/electric-vehicle-charging-device-statistics-january-2022.ods',
                                  r'C:\Users\Win 10 user\OneDrive\EV Dashboard\Source Data\Charge Points', 'EVCD_01a', 'TotalDevices')
    total_devices_df, per_100k_df_total = evcp_data_total.clean_data()
    evcp_data_total.write_date(total_devices_df, per_100k_df_total, 'charge_points_devices_total.csv', 'charge_points_per_100k_total.csv')

    evcp_data_rapid = EVCPDataExtractor(
        'https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1048354/electric-vehicle-charging-device-statistics-january-2022.ods',
        r'C:\Users\Win 10 user\OneDrive\EV Dashboard\Source Data\Charge Points', 'EVCD_01b', 'RapidDevices')
    rapid_devices_df, per_100k_df_rapid = evcp_data_rapid.clean_data()
    evcp_data_rapid.write_date(rapid_devices_df, per_100k_df_rapid, 'charge_points_devices_rapid.csv',
                               'charge_points_per_100k_rapid.csv')




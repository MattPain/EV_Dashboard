import pandas as pd

class EVDataExtractor:

    '''
    This class extracts Electric Vehicle Registration Data from the Department for Transport's website
    and writes the data to a chosen target directory. The script un-pivots the data for use in reporting and filtering,
    Primarily for the use of the EV infrastructure planning tool. The script extracts the whole dataset and outputs
    one sheet at a time into the target destination.

    The data is updated quarterly. Latest data is 2021 Q3.

    The source metadata can be seen below:
    - url = 'https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1046001/veh0132.ods'
    - file type = .ods (read with excel)
    - sheet names = VEH0132a_All, VEH0132b_BEV, VEH0132c_PHEV, VEH0132d_All_Private, VEH0132e_BEV_Private, VEH0132f_PHEV_Private,
                    VEH0132g_All_Company, VEH0132h_BEV_Company, VEH0132i_PHEV_Company
    - field names = ONS LA Code (April-2019), Region/Local Authority (Apr-2019), other field names are dates from 2011 Q4 - 2021 Q3

    Glossary:
    ULEV - Ultra Low Emission Vehicles
    PHEV - Plug in Hybrid Electric Vehicles (Subset of ULEV)
    BEV - Battery Electric Vehicle (subset of ULEV)
    ONS - Office for National Statistics

    Note that the sum of PHEV and BEV will not equal ULEV. This is a known issue in the dataset
    and the DfT have been made aware.
    '''

    header_names = ['LA/RegionCode', 'LA/RegionName']
    skip_rows = 6
    skip_footer = 14

    def __init__(self, source_url: str, sink_url: str, sheet_name: str, value_name: str):
        self.source_url = source_url
        self.sink_url = sink_url
        self.sheet_name = sheet_name
        self.value_name = value_name

    def clean_data(self):
        df = pd.read_excel(self.source_url, sheet_name=self.sheet_name, skiprows=6, skipfooter=14)

        df.rename(mapper={df.columns[0]: self.header_names[0], df.columns[1]: self.header_names[1]},
                  inplace=True, axis=1)

        df_pivoted = df.melt(id_vars=self.header_names, var_name='Date', value_name=self.value_name)

        df_pivoted['LA/RegionName'] = df_pivoted['LA/RegionName'].apply(lambda x: x.strip())
        df_pivoted['LA/RegionName'] = df_pivoted['LA/RegionName'].apply(lambda x: x.lower())
        df_pivoted['LA/RegionName'] = df_pivoted['LA/RegionName'].apply(lambda x: x.title())

        df_pivoted[self.value_name].replace('c', 0.0, inplace=True)

        df_pivoted[self.value_name] = df_pivoted[self.value_name].apply(lambda x: int(x))

        return df_pivoted

    def write_date(self, dataframe, file_name):
        dataframe.to_csv(self.sink_url + '\\' + file_name)
        # Add in write to database

if __name__ == '__main__':
    total_ulev_data = EVDataExtractor('https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1046001/veh0132.ods',
                                      r'C:\Users\Win 10 user\OneDrive\EV Dashboard\Source Data\Charge Points', 'VEH0132a_All',
                                      'ULEVRegistrations')
    total_ulev_df = total_ulev_data.clean_data()
    total_ulev_data.write_date(total_ulev_df, 'ev_registrations_ulev.csv')

    total_bev_data = EVDataExtractor(
        'https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1046001/veh0132.ods',
        r'C:\Users\Win 10 user\OneDrive\EV Dashboard\Source Data\Charge Points', 'VEH0132b_BEV',
        'BEVRegistrations')
    total_bev_df = total_bev_data.clean_data()
    total_bev_data.write_date(total_bev_df, 'ev_registrations_bev.csv')

    total_phev_data = EVDataExtractor(
        'https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1046001/veh0132.ods',
        r'C:\Users\Win 10 user\OneDrive\EV Dashboard\Source Data\Charge Points', 'VEH0132c_PHEV',
        'PHEVRegistrations')
    total_phev_df = total_phev_data.clean_data()
    total_phev_data.write_date(total_phev_df, 'ev_registrations_phev.csv')











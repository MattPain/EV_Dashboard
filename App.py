import dash
from dash import Input, Output, dcc, html
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import geopandas

# Data imports
evcp_data_directory = r'C:\Users\Win 10 user\OneDrive\EV Dashboard\Source Data\Charge Points'
ev_registrations_directory = r'C:\Users\Win 10 user\OneDrive\EV Dashboard\Source Data\EV Registrations'
geo_data_uk_districts = r'C:\Users\Win 10 user\OneDrive\EV Dashboard\Source Data\GeoJSON UK Districts\Local_Authority_Districts_(December_2020)_UK_BFC_v1.2.geojson'

# EVCP data
df_evcp_total = pd.read_csv(evcp_data_directory + '\\' + 'charge_points_devices_total.csv')
df_evcp_rapid = pd.read_csv(evcp_data_directory + '\\' + 'charge_points_devices_rapid.csv')
df_evcp_total_pop = pd.read_csv(evcp_data_directory + '\\' + 'charge_points_per_100k_total.csv')
df_evcp_rapid_pop = pd.read_csv(evcp_data_directory + '\\' + 'charge_points_per_100k_rapid.csv')

# EV data
df_ulev_total = pd.read_csv(ev_registrations_directory + '\\' + 'ev_registrations_ulev.csv')
df_phev_total = pd.read_csv(ev_registrations_directory + '\\' + 'ev_registrations_phev.csv')
df_bev_total = pd.read_csv(ev_registrations_directory + '\\' + 'ev_registrations_bev.csv')

# Geo JSON data - UK Districts
uk_districts = geopandas.read_file(geo_data_uk_districts)
uk_districts.to_crs(epsg=4326, inplace=True)

# Generate dropdown lists
location_options_list = [{'label' : name, 'value': name} for name in df_ulev_total['LA/RegionName'].unique()]
evcp_dates_options_list = [{'label' : name, 'value': name} for name in df_evcp_total['Date'].unique()]
ev_dates_options_list = [{'label' : name, 'value': name} for name in df_ulev_total['Date'].unique()]
map_options_list = [{'label': 'Map 1: Total ULEVs', 'value': 'Map1'},
                    {'label': 'Map 2: Total PHEVs', 'value': 'Map2'},
                    {'label': 'Map 3: Total BEVs', 'value': 'Map3'},
                    {'label': 'Map 4: Total EVCPs', 'value': 'Map4'},
                    {'label': 'Map 5: Rapid EVCPs', 'value': 'Map5'},
                    {'label': 'Map 6: Total Per100K EVCPS', 'value': 'Map6'},
                    {'label': 'Map 7: Rapid Per100K EVCPS', 'value': 'Map7'}]
ev_options_list = [{'label': 'EV Chart 1: ULEV', 'value': 'ULEV'},
                   {'label': 'EV Chart 2: PHEV', 'value': 'PHEV'},
                   {'label': 'EV Chart 3: BEV', 'value': 'BEV'}]
evcp_options_list = [{'label': 'EVCP Chart 1: Total Devices', 'value': 'total'},
                     {'label': 'EVCP Chart 2: Rapid Devices', 'value': 'rapid'}]

# Get date marks - evcp
marks = {i: label for i, label in zip(range(9), list(df_evcp_total['Date'].unique())[::-1])}

# Get date marks - ev
marks_ev = {i : label for i, label in zip(range(len(df_ulev_total['Date'].unique())), list(df_ulev_total['Date'].unique())[::-1])}

# Helper functions
def date_lookup_func(x):
    for v ,i in marks.items():
        if i == x:
            return int(v)

def date_lookup_func_ev(x):
    for v ,i in marks_ev.items():
        if i == x:
            return int(v)

# Initialise app
app = dash.Dash(__name__)

# Set app layout
app.layout = (html.Div(className='grid-container', children=[
    html.Div(className='header-container', children=[
        html.H1(className='dashboard-title',children='Electric Vehicle Registrations and Charge Points in the UK'),
        html.Div(className='stamp', children=[
            html.Div(className='stamp-title', children='ULEV Registrations Change - Total', id='ev-total-stamp-title'),
            html.Div(id='ev-total-change-container', className='stamp-content-container'),
            html.Div(id='ev-total-change-container-information', className='stamp-information')
        ]),
        html.Div(className='stamp', children=[
            html.Div(className='stamp-title', children='ULEV Registrations Change - %', id='ev-percent-stamp-title'),
            html.Div(id='ev-percent-change-container', className='stamp-content-container'),
            html.Div(id='ev-percent-change-container-information', className='stamp-information')
        ]),
        html.Div(className='stamp', children=[
            html.Div(className='stamp-title', children='EV Charge Points Change - Total', id='evcp-total-stamp-title'),
            html.Div(id='evcp-total-change-container', className='stamp-content-container'),
            html.Div(id='evcp-total-change-container-information', className='stamp-information')
        ]),
        html.Div(className='stamp', children=[
            html.Div(className='stamp-title', children='EV Charge Points Change - %', id='evcp-percent-stamp-title'),
            html.Div(id='evcp-percent-change-container', className='stamp-content-container'),
            html.Div(id='evcp-percent-change-container-information', className='stamp-information')
        ])
    ]),
    html.Div(className='info-filters-container', children=[
        html.H2(className='dropdown-title', children='Chart Controls'),
        dcc.Dropdown(id='ev-chart-selection-dropdown', value='ULEV', options=ev_options_list),
        dcc.Dropdown(id='evcp-chart-selection-dropdown', value='total', options=evcp_options_list),
        dcc.Dropdown(options=location_options_list, id='location-dropdown', value=['Great Britain'], multi=True),
        html.H2(className='dropdown-title', children='Map Controls'),
        dcc.Dropdown(id='map-chart-select-dropdown', options=map_options_list, value='Map1', style={'display': 'grid'}),
        dcc.Dropdown(id='map-dropdown-ev', options=ev_dates_options_list, value='2021 Q3', style={'display': 'grid'}),
        dcc.Dropdown(id='map-dropdown-evcp', options=evcp_dates_options_list, value='Jan-22', style={'display': 'none'})
    ]),
    html.Div(className='map-1-container', children=[
        dcc.Graph(id='map', style={'margin': 2, 'fontFamily': 'Sans Serif', 'fontSize': 'large'})
    ]),
    html.Div(className='line-chart-ev-container', children=[
        dcc.Graph(id='ev-chart', style={'margin': 5, 'fontFamily': 'sans serif', 'fontSize': 'large'}),
        dcc.RangeSlider(id='ev-date-slider',min=0, max=39, step=1, marks=marks_ev, value=[0, 39])
    ]),
    html.Div(className='line-chart-evcp-container', children=[
        dcc.Graph(id='evcp-chart', style={'margin': 2, 'marginBottom': 0, 'fontFamily': 'sans serif', 'fontSize': 'large'}),
        dcc.RangeSlider(id='evcp-date-slider',min=0, max=8, step=1, marks=marks, value=[0, 8])
    ])
]))

# Set callback functions

@app.callback(Output('ev-chart', 'figure'),
              [Input('location-dropdown', 'value'), Input('ev-date-slider', 'value'), Input('ev-chart-selection-dropdown', 'value')])
def update_ev_chart(location, date, ev_chart_selection):
    def set_dataframe(dataframe):
        df = dataframe.copy()
        df['DateLookUp'] = df['Date'].apply(date_lookup_func_ev)
        df = df.loc[df['DateLookUp'].between(date[0], date[1])]
        return df

    def set_charts(dataframe, x_axis_value, title):
        traces = [go.Scatter(x=dataframe.loc[dataframe['LA/RegionName'] == loc]['Date'],
                             y=dataframe.loc[dataframe['LA/RegionName'] == loc][x_axis_value], name=loc, line={'width': 5}) for
                  loc in location]

        layout = go.Layout(hovermode='x', font={'family': 'sans-serif', 'size': 15}, xaxis={'showgrid': False},
                           yaxis={'showgrid': True, 'gridcolor': '#eeeeee'}, plot_bgcolor='white',
                           title=f'<b>{title}</b>')
        fig = go.Figure(data=traces, layout=layout)
        fig['layout']['xaxis']['autorange'] = "reversed"

        return fig

    if ev_chart_selection == 'ULEV':
        df_ev = set_dataframe(df_ulev_total)
        fig = set_charts(df_ev, 'ULEVRegistrations', 'ULEV Registrations by Location, Quarter and Year')
        return fig

    if ev_chart_selection == 'PHEV':
        df_ev = set_dataframe(df_phev_total)
        fig = set_charts(df_ev, 'PHEVRegistrations', 'PHEV Registrations by Location, Quarter and Year')
        return fig

    if ev_chart_selection == 'BEV':
        df_ev = set_dataframe(df_bev_total)
        fig = set_charts(df_ev, 'BEVRegistrations', 'BEV Registrations by Location, Quarter and Year')
        return fig




@app.callback(Output('evcp-chart', 'figure'),
              [Input('location-dropdown', 'value'), Input('evcp-date-slider', 'value'), Input('evcp-chart-selection-dropdown', 'value')])
def updated_evcp_chart(location, date, evcp_chart_selection):
    def set_dataframe(dataframe):

        df = dataframe.copy()
        df['DateLookUp'] = df['Date'].apply(date_lookup_func)
        df = df.loc[df['DateLookUp'].between(date[0], date[1])]

        return df

    def set_charts(dataframe, x_axis_value, title):
        traces = [go.Scatter(x=dataframe.loc[dataframe['LA/RegionName'] == loc]['Date'],
                             y=dataframe.loc[dataframe['LA/RegionName'] == loc][x_axis_value], name=loc, line={'width': 5}) for loc in location]

        layout = go.Layout(hovermode='x', font={'family':'sans-serif', 'size': 15}, xaxis={'showgrid': False},
                           yaxis={'showgrid': True, 'gridcolor': '#eeeeee'}, plot_bgcolor='white',
                           title=f'<b>{title}</b>')
        fig = go.Figure(data=traces, layout=layout)
        fig['layout']['xaxis']['autorange'] = "reversed"

        return fig

    if evcp_chart_selection == 'total':
        df = set_dataframe(df_evcp_total)
        fig = set_charts(df, 'TotalDevices', 'Total Electric Vehicle Charge Points by Location, Month and Year')
        return fig

    if evcp_chart_selection == 'rapid':
        df = set_dataframe(df_evcp_rapid)
        fig = set_charts(df, 'RapidDevices', 'Rapid Electric Vehicle Charge Points by Location, Month and Year')
        return fig

@app.callback([Output('map', 'figure'), Output('map-dropdown-ev', 'style'), Output('map-dropdown-evcp', 'style')],
              [Input('map-dropdown-ev', 'value'), Input('map-dropdown-evcp', 'value'),
               Input('map-chart-select-dropdown', 'value')])
def update_map(ev_date, evcp_date, map_option):

    def set_df(dataframe, date, continuous_data_column_name):
        df = dataframe.copy()
        df = df.loc[df['Date'] == date][['LA/RegionCode', continuous_data_column_name]]
        gdf_joined = pd.merge(left=uk_districts, right=df, left_on='LAD20CD', right_on='LA/RegionCode', how='left')
        gdf_joined.set_index('OBJECTID', inplace=True)
        gdf_joined.dropna(inplace=True)
        return gdf_joined

    def set_map(dataframe, color_scale, hover_data, title):
        fig = px.choropleth_mapbox(dataframe,
                                   geojson=dataframe.geometry,
                                   locations=dataframe.index,
                                   color=color_scale,
                                   color_continuous_scale=px.colors.sequential.Rainbow,
                                   mapbox_style='open-street-map',
                                   center={'lat': 55.3781, 'lon': -3.4360}, zoom=5,
                                   hover_data=hover_data,
                                   title=f'<b>{title}</b>')

        fig.update_geos(fitbounds="geojson")
        fig.update_layout(font={'size': 16, 'family': 'sans-serif'}, coloraxis_colorbar={'title': None})

        return fig

    if map_option == 'Map1':
        gdf_joined = set_df(df_ulev_total, ev_date, 'ULEVRegistrations')

        fig = set_map(gdf_joined, 'ULEVRegistrations', [gdf_joined['LAD20NM'],
                      gdf_joined['ULEVRegistrations']], 'Total ULEV Registrations by LAD, Quarter and Year')
        return fig, {'display': 'grid'}, {'display': 'none'}

    if map_option == 'Map2':
        gdf_joined = set_df(df_phev_total, ev_date, 'PHEVRegistrations')

        fig = set_map(gdf_joined, 'PHEVRegistrations', [gdf_joined['LAD20NM'], gdf_joined['PHEVRegistrations']],
                      'Total PHEV Registrations by LAD, Quarter and Year')
        return fig, {'display': 'grid'}, {'display': 'none'}

    if map_option == 'Map3':
        gdf_joined = set_df(df_bev_total, ev_date, 'BEVRegistrations')

        fig = set_map(gdf_joined, 'BEVRegistrations', [gdf_joined['LAD20NM'], gdf_joined['BEVRegistrations']],
                      'Total BEV Registrations by LAD, Quarter and Year')
        return fig, {'display': 'grid'}, {'display': 'none'}

    if map_option == 'Map4':
        gdf_joined = set_df(df_evcp_total, evcp_date, 'TotalDevices')

        fig = set_map(gdf_joined, 'TotalDevices', [gdf_joined['LAD20NM'], gdf_joined['TotalDevices']],
                      'Total EV Charge Points by LAD, Month and Year')
        return fig, {'display': 'none'}, {'display': 'grid'}

    if map_option == 'Map5':
        gdf_joined = set_df(df_evcp_rapid, evcp_date, 'RapidDevices')

        fig = set_map(gdf_joined, 'RapidDevices', [gdf_joined['LAD20NM'], gdf_joined['RapidDevices']],
                      'Rapid EV Charge Points by LAD, Month and Year')
        return fig, {'display': 'none'}, {'display': 'grid'}

    if map_option == 'Map6':
        gdf_joined = set_df(df_evcp_total_pop, evcp_date, 'Per100kPop')

        fig = set_map(gdf_joined, 'Per100kPop', [gdf_joined['LAD20NM'], gdf_joined['Per100kPop']],
                      'Total EV Charge Points per 100k Population by LAD, Month and Year')
        return fig, {'display': 'none'}, {'display': 'grid'}

    if map_option == 'Map7':
        gdf_joined = set_df(df_evcp_rapid_pop, evcp_date, 'Per100kPop')

        fig = set_map(gdf_joined, 'Per100kPop', [gdf_joined['LAD20NM'], gdf_joined['Per100kPop']],
                      'Rapid EV Charge Points per 100k Population by LAD, Month and Year')
        return fig, {'display': 'none'}, {'display': 'grid'}

@app.callback([Output('ev-total-change-container', 'children'), Output('ev-percent-change-container', 'children'),
               Output('ev-total-change-container-information', 'children'), Output('ev-percent-change-container-information', 'children'),
               Output('ev-total-stamp-title', 'children'), Output('ev-percent-stamp-title', 'children')],
              [Input('location-dropdown', 'value'), Input('ev-date-slider', 'value'), Input('ev-chart-selection-dropdown', 'value')])
def update_stamps_ev(location, ev_time_period, ev_chart_selection):

    def set_ev_stamp(dataframe, x_axis_value):
        df_ev = dataframe.copy()
        df_ev['DateLookUp'] = df_ev['Date'].apply(date_lookup_func_ev)

        end_value_ev = df_ev.loc[(df_ev['LA/RegionName'] == location[0]) & (df_ev['DateLookUp'] == ev_time_period[0])][
            x_axis_value].iloc[0]

        end_date_ev = \
        df_ev.loc[(df_ev['LA/RegionName'] == location[0]) & (df_ev['DateLookUp'] == ev_time_period[0])]['Date'].iloc[0]

        start_value_ev = \
        df_ev.loc[(df_ev['LA/RegionName'] == location[0]) & (df_ev['DateLookUp'] == ev_time_period[1])][
            x_axis_value].iloc[0]

        start_date_ev = df_ev.loc[(df_ev['LA/RegionName'] == location[0]) & (df_ev['DateLookUp'] == ev_time_period[1])][
            'Date'].iloc[0]

        if start_value_ev < 1:
            start_value_ev = 1

        total_ev_string = f'{start_value_ev - end_value_ev}'
        percent_ev_string = f'{int(round(((start_value_ev - end_value_ev) / end_value_ev) * 100, 0))}%'

        ev_information_string = f'{end_date_ev} - {start_date_ev} {location[0]}'

        return total_ev_string, percent_ev_string, ev_information_string, \
               ev_information_string

    if ev_chart_selection == 'ULEV':
        if len(location) < 1:
            return '-', '-', '-', '-', '-', '-'
        total_ev_string, percent_ev_string, ev_information_string, \
               ev_information_string = set_ev_stamp(df_ulev_total, 'ULEVRegistrations')

        stamp_title_total = 'ULEV Registrations Change - Total'
        stamp_title_percent = 'ULEV Registrations Change - %'
        return total_ev_string, percent_ev_string, ev_information_string, \
               ev_information_string, stamp_title_total, stamp_title_percent

    if ev_chart_selection == 'PHEV':
        if len(location) < 1:
            return '-', '-', '-', '-', '-', '-'
        total_ev_string, percent_ev_string, ev_information_string, \
               ev_information_string = set_ev_stamp(df_phev_total, 'PHEVRegistrations')

        stamp_title_total = 'PHEV Registrations Change - Total'
        stamp_title_percent = 'PHEV Registrations Change - %'
        return total_ev_string, percent_ev_string, ev_information_string, \
               ev_information_string, stamp_title_total, stamp_title_percent

    if ev_chart_selection == 'BEV':
        if len(location) < 1:
            return '-', '-', '-', '-', '-', '-'
        total_ev_string, percent_ev_string, ev_information_string, \
               ev_information_string = set_ev_stamp(df_bev_total, 'BEVRegistrations')

        stamp_title_total = 'BEV Registrations Change - Total'
        stamp_title_percent = 'BEV Registrations Change - %'
        return total_ev_string, percent_ev_string, ev_information_string, \
               ev_information_string, stamp_title_total, stamp_title_percent




@app.callback([Output('evcp-total-change-container', 'children'), Output('evcp-percent-change-container', 'children'),
               Output('evcp-total-change-container-information', 'children'),
               Output('evcp-percent-change-container-information', 'children'), Output('evcp-total-stamp-title', 'children'),
               Output('evcp-percent-stamp-title', 'children')],
              [Input('location-dropdown', 'value'), Input('evcp-date-slider', 'value'), Input('evcp-chart-selection-dropdown', 'value')])
def update_stamps_evcp(location, evcp_time_period, evcp_chart_selection):
    def set_evcp_stamp(dataframe, x_axis_value):
        df_evcp = dataframe.copy()

        df_evcp['DateLookUp'] = df_evcp['Date'].apply(date_lookup_func)

        end_value_evcp = \
        df_evcp.loc[(df_evcp['LA/RegionName'] == location[0]) & (df_evcp['DateLookUp'] == evcp_time_period[0])][x_axis_value].iloc[0]

        end_date_evcp = \
        df_evcp.loc[(df_evcp['LA/RegionName'] == location[0]) & (df_evcp['DateLookUp'] == evcp_time_period[0])][
            'Date'].iloc[0]

        start_value_evcp = \
        df_evcp.loc[(df_evcp['LA/RegionName'] == location[0]) & (df_evcp['DateLookUp'] == evcp_time_period[1])][
            x_axis_value].iloc[0]

        start_date_evcp = \
        df_evcp.loc[(df_evcp['LA/RegionName'] == location[0]) & (df_evcp['DateLookUp'] == evcp_time_period[1])][

            'Date'].iloc[0]

        if start_value_evcp < 1:
            start_value_evcp = 1

        total_evcp_string = f'{start_value_evcp - end_value_evcp}'
        percent_evcp_string = f'{int(round(((start_value_evcp - end_value_evcp) / end_value_evcp) * 100, 0))}%'
        evcp_information_string = f'{end_date_evcp} - {start_date_evcp} {location[0]}'

        return total_evcp_string, percent_evcp_string, evcp_information_string, evcp_information_string

    if evcp_chart_selection == 'total':
        if len(location) < 1:
            return '-', '-', '-', '-', '-', '-'
        total_evcp_string, percent_evcp_string, evcp_information_string, evcp_information_string = set_evcp_stamp(df_evcp_total, 'TotalDevices')
        stamp_title_total = 'Total Charge Points Change - Total'
        stamp_title_percent = 'Total Charge Points Change - %'
        return total_evcp_string, percent_evcp_string, evcp_information_string, evcp_information_string, stamp_title_total, stamp_title_percent

    if evcp_chart_selection == 'rapid':
        if len(location) < 1:
            return '-', '-', '-', '-', '-', '-'
        total_evcp_string, percent_evcp_string, evcp_information_string, evcp_information_string = set_evcp_stamp(df_evcp_rapid, 'RapidDevices')
        stamp_title_total = 'Rapid Charge Points Change - Total'
        stamp_title_percent = 'Rapid Charge Points Change - %'
        return total_evcp_string, percent_evcp_string, evcp_information_string, evcp_information_string, stamp_title_total, stamp_title_percent


if __name__ == '__main__':
    app.run_server(debug=True)
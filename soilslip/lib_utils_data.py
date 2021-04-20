# -------------------------------------------------------------------------------------
# Libraries
import logging

import numpy as np
import pandas as pd

from copy import deepcopy
from lib_analysis_interpolation_point import interp_point2grid

# Default variable(s)
lut_season_default = {
    1: 'DJF', 2: 'DJF',
    3: 'MAM', 4: 'MAM', 5: 'MAM',
    6: 'JJA', 7: 'JJA', 8: 'JJA',
    9: 'SON', 10: 'SON', 11: 'SON',
    12: 'DJF'
}
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to filter scenarios dataframe
def filter_scenarios_dataframe(df_scenarios,
                               tag_column_rain='rain_accumulated_3H', tag_time='time',filter_rain=True,
                               value_min_rain=0, value_max_rain=None,
                               tag_column_sm='sm_max', filter_sm=True,
                               value_min_sm=0, value_max_sm=1,
                               tag_column_event='event_n', filter_event=True,
                               value_min_event=1, value_max_event=None,
                               tag_column_season='seasons', filter_season=True,
                               season_lut=None, season_name='ALL'):

    dframe_scenarios = deepcopy(df_scenarios)

    if not isinstance(tag_column_rain, list):
        tag_column_rain = [tag_column_rain]
    if not isinstance(tag_column_sm, list):
        tag_column_sm = [tag_column_sm]

    if filter_season:
        if season_lut is not None:
            grp_season = [season_lut.get(pd.Timestamp(t_stamp).month) for t_stamp in dframe_scenarios[tag_time].values]
            dframe_scenarios[tag_column_season] = grp_season
        else:
            dframe_scenarios[tag_column_season] = 'ALL'
    else:
        dframe_scenarios[tag_column_season] = 'ALL'

    # Filter by rain not valid values
    if filter_rain:
        for tag_column_step in tag_column_rain:
            logging.info(' -------> Filter variable ' + tag_column_step + ' ... ')
            if tag_column_step in list(dframe_scenarios.columns):
                if value_min_rain is not None:
                    dframe_scenarios = dframe_scenarios.drop(dframe_scenarios[dframe_scenarios[tag_column_step] < value_min_rain].index)
                if value_max_rain is not None:
                    dframe_scenarios = dframe_scenarios.drop(dframe_scenarios[dframe_scenarios[tag_column_step] > value_max_rain].index)
                logging.info(' -------> Filter variable ' + tag_column_step + ' ... DONE')
            else:
                logging.info(' -------> Filter variable ' + tag_column_step + ' ... FAILED')
                logging.warning(' ===> Filter rain datasets failed. Variable ' + tag_column_step +
                                ' is not in the selected dataframe')

    # Filter by soil moisture not valid values
    if filter_sm:
        for tag_column_step in tag_column_sm:
            logging.info(' -------> Filter variable ' + tag_column_step + ' ... ')
            if tag_column_step in list(dframe_scenarios.columns):
                if value_min_sm is not None:
                    dframe_scenarios = dframe_scenarios.drop(dframe_scenarios[dframe_scenarios[tag_column_step] < value_min_sm].index)
                if value_max_sm is not None:
                    dframe_scenarios = dframe_scenarios.drop(dframe_scenarios[dframe_scenarios[tag_column_step] > value_max_sm].index)
                logging.info(' -------> Filter variable ' + tag_column_step + ' ... DONE')
            else:
                logging.info(' -------> Filter variable ' + tag_column_step + ' ... FAILED')
                logging.warning(' ===> Filter soil moisture datasets failed. Variable ' + tag_column_step +
                                ' is not in the selected dataframe')

    # Filter by event n
    if filter_event:
        if value_min_event is not None:
            dframe_scenarios = dframe_scenarios.drop(dframe_scenarios[dframe_scenarios[tag_column_event] < value_min_event].index)
        if value_max_event is not None:
            dframe_scenarios = dframe_scenarios.drop(dframe_scenarios[dframe_scenarios[tag_column_event] > value_max_event].index)

    # Filter by season name
    if filter_season:
        dframe_scenarios = dframe_scenarios.loc[dframe_scenarios[tag_column_season] == season_name]

    return dframe_scenarios
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to filter rain dataframe
def filter_rain_dataframe(df_rain, dict_point_static=None, tag_filter_column='code'):

    dict_point_dynamic = {}
    for point_reference, point_fields in dict_point_static.items():
        point_neighbour_code = point_fields[tag_filter_column]
        df_select = df_rain.loc[df_rain[tag_filter_column].isin(point_neighbour_code)]
        dict_point_dynamic[point_reference] = df_select
    return dict_point_dynamic
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to interpolate rain dataframe
def interpolate_rain_dataframe(df_rain, mask_out_2d, geox_out_2d, geoy_out_2d, folder_tmp=None):

    geox_in_1d = df_rain['longitude'].values
    geoy_in_1d = df_rain['latitude'].values
    data_in_1d = df_rain['data'].values

    data_out_2d = interp_point2grid(
        data_in_1d, geox_in_1d, geoy_in_1d, geox_out_2d, geoy_out_2d, epsg_code='4326',
        interp_no_data=-9999.0, interp_radius_x=0.2, interp_radius_y=0.2,
        interp_method='idw', var_name_data='values', var_name_geox='x', var_name_geoy='y',
        folder_tmp=folder_tmp)

    data_out_2d[mask_out_2d == 0] = np.nan

    return data_out_2d
# -------------------------------------------------------------------------------------

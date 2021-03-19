# -------------------------------------------------------------------------------------
# Libraries
import logging

from copy import deepcopy

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
                               tag_column_rain='rain_accumulated_3H', filter_rain=True,
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
            grp_season = [season_lut.get(t_stamp.month) for t_stamp in dframe_scenarios.index]
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

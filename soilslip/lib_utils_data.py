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
                               tag_column_rain='rain', filter_rain=True, value_min_rain=0, value_max_rain=None,
                               tag_column_sm='soil_moisture', filter_sm=True, value_min_sm=0, value_max_sm=1,
                               tag_column_event='event_n', filter_event=True, value_min_event=1, value_max_event=None,
                               tag_column_season='seasons', filter_season=True,
                               season_lut=None, season_name='ALL'):

    dframe_scenarios = deepcopy(df_scenarios)

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
        if value_min_rain is not None:
            dframe_scenarios = dframe_scenarios.drop(dframe_scenarios[dframe_scenarios[tag_column_rain] < value_min_rain].index)
        if value_max_rain is not None:
            dframe_scenarios = dframe_scenarios.drop(dframe_scenarios[dframe_scenarios[tag_column_rain] > value_max_rain].index)

    # Filter by soil moisture not valid values
    if filter_sm:
        if value_min_sm is not None:
            dframe_scenarios = dframe_scenarios.drop(dframe_scenarios[dframe_scenarios[tag_column_sm] < value_min_sm].index)
        if value_max_sm is not None:
            dframe_scenarios = dframe_scenarios.drop(dframe_scenarios[dframe_scenarios[tag_column_sm] > value_max_sm].index)

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

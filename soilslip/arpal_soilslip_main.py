#!/usr/bin/python3
"""
ARPAL Processing Tool - SOIL SLIPS

__date__ = '20210412'
__version__ = '1.3.0'
__author__ =
        'Fabio Delogu (fabio.delogu@cimafoundation.org',
        'Michele Cicoria (michele.cicoria@arpal.liguria.it)',
        'Monica Solimano (monica.solimano@arpal.liguria.it)'

__library__ = 'ARPAL'

General command line:
python3 arpal_soilslip_main.py -settings_file configuration.json -time "YYYY-MM-DD HH:MM"

Version(s):
20210412 (1.3.0) --> Add dependencies management, add forcing point creation for saving rain peaks
20210319 (1.2.1) --> Fix bugs in creating output indicators workspace files and csv and png scenarios files
20210202 (1.2.0) --> Fix bugs in creating rain datasets; fix bugs in output csv scenarios files
20201125 (1.1.0) --> Update of reader and writer methods for rain and soil moisture variables
20200515 (1.0.0) --> Beta release
"""

# -------------------------------------------------------------------------------------
# Complete library
import logging
import time
import os

from driver_data_io_geo_point_soil_slips import DriverGeoPoint as DriverGeoPoint_SoilSlips
from driver_data_io_geo_point_weather_stations import DriverGeoPoint as DriverGeoPoint_WeatherStations
from driver_data_io_geo_grid import DriverGeoGrid
from driver_data_io_forcing_rain import DriverForcing as DriverForcingRain
from driver_data_io_forcing_sm import DriverForcing as DriverForcingSM
from driver_analysis_indicators import DriverAnalysis as DriverAnalysisIndicators
from driver_analysis_scenarios import DriverAnalysis as DriverAnalysisScenarios

from argparse import ArgumentParser

from lib_utils_io import read_file_json
from lib_utils_system import make_folder
from lib_utils_time import set_time
# -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------
# Algorithm information
alg_version = '1.2.1'
alg_release = '2021-03-19'
alg_name = 'SOIL SLIPS MAIN'
# Algorithm parameter(s)
time_format = '%Y-%m-%d %H:%M'
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Script Main
def main():

    # -------------------------------------------------------------------------------------
    # Get algorithm settings
    alg_settings, alg_time = get_args()

    # Set algorithm settings
    data_settings = read_file_json(alg_settings)

    # Set algorithm logging
    make_folder(data_settings['data']['log']['folder_name'])
    set_logging(logger_file=os.path.join(data_settings['data']['log']['folder_name'],
                                         data_settings['data']['log']['file_name']))
    # Set algorithm library dependencies
    set_deps(data_settings['algorithm']['dependencies'], env_extra=['PROJ_LIB', 'GDAL_DATA'])
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Info algorithm
    logging.info(' ============================================================================ ')
    logging.info(' ==> ' + alg_name + ' (Version: ' + alg_version + ' Release_Date: ' + alg_release + ')')
    logging.info(' ==> START ... ')
    logging.info(' ')

    # Time algorithm information
    start_time = time.time()
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Organize time run
    time_run, time_range = set_time(
        time_run_args=alg_time,
        time_run_file=data_settings['time']['time_now'],
        time_run_file_start=data_settings['time']['time_start'],
        time_run_file_end=data_settings['time']['time_end'],
        time_format=time_format,
        time_period=data_settings['time']['time_period'],
        time_frequency=data_settings['time']['time_frequency'],
        time_rounding=data_settings['time']['time_rounding']
    )
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Geographical datasets
    driver_data_geo_grid = DriverGeoGrid(
        src_dict=data_settings['data']['static']['source'],
        dst_dict=data_settings['data']['static']['destination'],
        group_data=data_settings['algorithm']['ancillary']['group'],
        alg_template_tags=data_settings['algorithm']['template'],
        flag_geo_updating=data_settings['algorithm']['flags']['updating_static_data'])
    geo_data_collection = driver_data_geo_grid.organize_data()

    # Weather stations point datasets
    driver_data_geo_point_weather_stations = DriverGeoPoint_WeatherStations(
        src_dict=data_settings['data']['static']['source'],
        dst_dict=data_settings['data']['static']['destination'],
        group_data=data_settings['algorithm']['ancillary']['group'],
        alg_template_tags=data_settings['algorithm']['template'],
        flag_geo_updating=data_settings['algorithm']['flags']['updating_static_data'])
    geo_point_collection_weather_stations = driver_data_geo_point_weather_stations.organize_data()

    # Soil-slips point datasets
    driver_data_geo_point_soil_slips = DriverGeoPoint_SoilSlips(
        src_dict=data_settings['data']['static']['source'],
        dst_dict=data_settings['data']['static']['destination'],
        group_data=data_settings['algorithm']['ancillary']['group'],
        flag_geo_updating=data_settings['algorithm']['flags']['updating_static_data'])
    geo_point_collection_soil_slips = driver_data_geo_point_soil_slips.organize_data()
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Activate analyzer mode
    if activate_algorithm_step(['organizer', 'analyzer'], data_settings['algorithm']['flags']['running_mode']):

        # Iterate over time(s)
        for time_step in time_range:

            # Rain datasets
            driver_data_forcing_rain = DriverForcingRain(
                time_step,
                src_dict=data_settings['data']['dynamic']['source'],
                ancillary_dict=data_settings['data']['dynamic']['ancillary'],
                dst_dict=data_settings['data']['dynamic']['destination'],
                tmp_dict=data_settings['data']['tmp'],
                time_data=data_settings['data']['dynamic']['time'],
                geo_data_region=geo_data_collection['geo_region'],
                geo_data_weather_station=geo_point_collection_weather_stations,
                group_data=data_settings['algorithm']['ancillary']['group'],
                alg_template_tags=data_settings['algorithm']['template'],
                flag_ancillary_updating=data_settings['algorithm']['flags']['updating_dynamic_ancillary_rain'])
            if activate_algorithm_step(['organizer'], data_settings['algorithm']['flags']['running_mode']):
                driver_data_forcing_rain.organize_forcing()

            # Soil moisture datasets
            driver_data_forcing_sm = DriverForcingSM(
                time_step,
                src_dict=data_settings['data']['dynamic']['source'],
                ancillary_dict=data_settings['data']['dynamic']['ancillary'],
                dst_dict=data_settings['data']['dynamic']['destination'],
                time_data=data_settings['data']['dynamic']['time'],
                basin_data=geo_data_collection['geo_basin'],
                geo_data=geo_data_collection['geo_alert_area'],
                group_data=data_settings['algorithm']['ancillary']['group'],
                alg_template_tags=data_settings['algorithm']['template'],
                flag_ancillary_updating=data_settings['algorithm']['flags']['updating_dynamic_ancillary_sm'])
            if activate_algorithm_step(['organizer'], data_settings['algorithm']['flags']['running_mode']):
                driver_data_forcing_sm.organize_forcing()

            # Analysis datasets to define indicators
            driver_analysis_indicators = DriverAnalysisIndicators(
                time_step,
                file_list_rain_map=driver_data_forcing_rain.file_path_processed_map,
                file_list_rain_point=driver_data_forcing_rain.file_path_processed_point,
                file_list_sm=driver_data_forcing_sm.file_path_processed,
                ancillary_dict=data_settings['data']['dynamic']['ancillary'],
                dst_dict=data_settings['data']['dynamic']['destination'],
                time_data=data_settings['data']['dynamic']['time'],
                geo_data_region=geo_data_collection['geo_region'],
                geo_data_alert_area=geo_data_collection['geo_alert_area'],
                geo_data_weather_station=geo_point_collection_weather_stations,
                index_data_alert_area=geo_data_collection['index_alert_area'],
                group_data=data_settings['algorithm']['ancillary']['group'],
                alg_template_tags=data_settings['algorithm']['template'],
                flag_dest_updating=data_settings['algorithm']['flags']['updating_dynamic_indicators'])

            if activate_algorithm_step(['analyzer'], data_settings['algorithm']['flags']['running_mode']):
                analysis_data_rain_point = driver_analysis_indicators.organize_analysis_rain_point()
                analysis_data_rain_map = driver_analysis_indicators.organize_analysis_rain_map()
                analysis_data_sm = driver_analysis_indicators.organize_analysis_sm()

                driver_analysis_indicators.save_analysis(analysis_data_sm,
                                                         analysis_data_rain_map, analysis_data_rain_point,
                                                         geo_point_collection_soil_slips)
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Activate publisher mode
    if activate_algorithm_step(['publisher'], data_settings['algorithm']['flags']['running_mode']):

        # -------------------------------------------------------------------------------------
        # Analysis datasets to define scenarios
        driver_analysis_scenarios = DriverAnalysisScenarios(
            time_run, time_range,
            ancillary_dict=data_settings['data']['dynamic']['ancillary'],
            dst_dict=data_settings['data']['dynamic']['destination'],
            geo_data_region=driver_data_geo_grid.dset_geo_region,
            geo_data_alert_area=driver_data_geo_grid.dset_geo_alert_area,
            group_data=data_settings['algorithm']['ancillary']['group'],
            plot_data=data_settings['algorithm']['ancillary']['plot'],
            alg_template_tags=data_settings['algorithm']['template'],
            flag_dest_updating=data_settings['algorithm']['flags']['updating_dynamic_scenarios'])

        scenarios_data = driver_analysis_scenarios.collect_scenarios()
        driver_analysis_scenarios.dump_scenarios(scenarios_data)
        driver_analysis_scenarios.plot_scenarios(scenarios_data)
        # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # Info algorithm
    time_elapsed = round(time.time() - start_time, 1)

    logging.info(' ')
    logging.info(' ==> ' + alg_name + ' (Version: ' + alg_version + ' Release_Date: ' + alg_release + ')')
    logging.info(' ==> TIME ELAPSED: ' + str(time_elapsed) + ' seconds')
    logging.info(' ==> ... END')
    logging.info(' ==> Bye, Bye')
    logging.info(' ============================================================================ ')

    # -------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to activate algorithm part
def activate_algorithm_step(algorithm_mode_step, algorithm_mode_list, algorithm_mode_type='any'):
    if algorithm_mode_type == 'any':
        algorithm_mode_flag = any(item in algorithm_mode_step for item in algorithm_mode_list)
    elif algorithm_mode_type == 'all':
        algorithm_mode_flag = all(item in algorithm_mode_step for item in algorithm_mode_list)
    else:
        algorithm_mode_flag = any(item in algorithm_mode_step for item in algorithm_mode_list)
    return algorithm_mode_flag
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to set libraries dependencies
def set_deps(algorithm_deps, env_ld_library='LD_LIBRARY_PATH', env_path='PATH', env_extra=None):

    # ENV LD_LIBRARY_PATH
    deps_list = algorithm_deps[env_ld_library]
    if deps_list is not None:
        for deps_step in deps_list:
            if env_ld_library not in list(os.environ):
                os.environ[env_ld_library] = deps_step
            else:
                os.environ[env_ld_library] += os.pathsep + deps_step
    # ENV PATH
    deps_list = algorithm_deps[env_path]
    if deps_list is not None:
        for deps_step in deps_list:
            if env_path not in list(os.environ):
                os.environ[env_path] = deps_step
            else:
                os.environ[env_path] += os.pathsep + deps_step
    # ENV EXTRA (NOT PATH OR LD_LIBRARY_PATH)
    if env_extra is not None:
        for env_name in env_extra:
            env_value = algorithm_deps[env_name]
            if env_value is not None:
                os.environ[env_name] = env_value
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to get script argument(s)
def get_args():
    parser_handle = ArgumentParser()
    parser_handle.add_argument('-settings_file', action="store", dest="alg_settings")
    parser_handle.add_argument('-time', action="store", dest="alg_time")
    parser_values = parser_handle.parse_args()

    if parser_values.alg_settings:
        alg_settings = parser_values.alg_settings
    else:
        alg_settings = 'configuration.json'

    if parser_values.alg_time:
        alg_time = parser_values.alg_time
    else:
        alg_time = None

    return alg_settings, alg_time

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to set logging information
def set_logging(logger_file='log.txt', logger_format=None):
    if logger_format is None:
        logger_format = '%(asctime)s %(name)-12s %(levelname)-8s ' \
                        '%(filename)s:[%(lineno)-6s - %(funcName)20s()] %(message)s'

    # Remove old logging file
    if os.path.exists(logger_file):
        os.remove(logger_file)

    # Set level of root debugger
    logging.root.setLevel(logging.DEBUG)

    # Open logging basic configuration
    logging.basicConfig(level=logging.DEBUG, format=logger_format, filename=logger_file, filemode='w')

    # Set logger handle
    logger_handle_1 = logging.FileHandler(logger_file, 'w')
    logger_handle_2 = logging.StreamHandler()
    # Set logger level
    logger_handle_1.setLevel(logging.DEBUG)
    logger_handle_2.setLevel(logging.DEBUG)
    # Set logger formatter
    logger_formatter = logging.Formatter(logger_format)
    logger_handle_1.setFormatter(logger_formatter)
    logger_handle_2.setFormatter(logger_formatter)

    # Add handle to logging
    logging.getLogger('').addHandler(logger_handle_1)
    logging.getLogger('').addHandler(logger_handle_2)

# -------------------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Call script from external library
if __name__ == '__main__':
    main()
# ----------------------------------------------------------------------------

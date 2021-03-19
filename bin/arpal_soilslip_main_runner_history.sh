#!/bin/bash -e

#-----------------------------------------------------------------------------------------
# Script information
script_name='ARPAL - SOILSLIP SCENARIOS - RUNNER - HISTORY'
script_version="1.0.0"
script_date='2020/12/14'

# Script flag(s)
flag_execution=true

# Script Info
script_folder='/home/admin/library/arpal-dev/soilslip/'
script_file_main='/home/admin/library/arpal-dev/soilslip/arpal_soilsplip_main.py'
script_file_settings='/home/admin/soilslip-exec/arpal_soilslips_configuration.json'

# VirtualEnv Info
virtualenv_folder='/home/admin/library/virtualenv_python3/'
virtualenv_name='virtualenv_python3'
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Get information (-u to get gmt time)
#time_run=$(date -u +"%Y-%m-%d %H:00")
time_run="2019-06-01 00:00" # DEBUG ANALYSIS CASE
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Activate python miniconda virtualenv
export PATH=$virtualenv_folder/bin:$PATH
source activate $virtualenv_name
# Add path to pythonpath
export PYTHONPATH="${PYTHONPATH}:$script_folder"
#-----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Info script start
echo " ==================================================================================="
echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> START ..."

# Section to execute the soilslip procedure
echo " ====> COMPUTE SOILSLIP SCENARIOS ... "
if $flag_execution; then

    # Run python command line
    echo " =====> EXECUTE: " python $script_file_main -settings_file $script_file_settings -time $time_run
    python $script_file_main -settings_file $script_file_settings -time "$time_run"

    echo " ====> COMPUTE SOILSLIP SCENARIOS ... DONE"

else
    echo " ====> COMPUTE SOILSLIP SCENARIOS ... SKIPPED. FLAG NOT ACTIVATED"
fi

# Info script end
echo " ==> ... END"
echo " ==> Bye, Bye"
echo " ==================================================================================="
# ----------------------------------------------------------------------------------------







#!/bin/bash -e

#-----------------------------------------------------------------------------------------
# Script information
script_name='ARPAL - SOILSLIP SCENARIOS - ORGANIZER SOIL MOISTURE - HISTORY'
script_version="1.0.0"
script_date='2020/12/14'

time_period_download=2400 # days(s)

domain_list=(
"Tanaro" "Savonese" "Ponente" "Imperiese" "Finalese" "OrbaStura" 
"CentroPonente" "Centa" "LevanteGenovese" "Erro" "Entella" "BormidaS" "BormidaM" "AvetoTrebbia" 
"PonenteGenovese" "Magra" "Scrivia" "Entella"
)

# Dynamic folder(s) 
folder_data_source_raw="/home/admin/soilslip-ws/dynamic/source/soil_moisture/%DOMAIN_NAMEDomain/"
folder_data_destination_raw="/home/admin/soilslip-ws/dynamic/source/soil_moisture/%DOMAIN_NAMEDomain/%Y/%m/"

file_data_raw="%DOMAIN_NAMEDomainV_%Y%m%d2300.gz"
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Get information (-u to get gmt time)
time_run="2020-02-01 00:00" # DEBUG DATABASE CASE
#-----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Info script start
echo " ==================================================================================="
echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> START ..."

# Iterate over domain and period
time_run=$(date -d "$time_run" +'%Y-%m-%d %H:00')
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Section to dowload dynamic datasets from remote machine to local machine
echo " ===> MOVE DYNAMIC DATA ... "

# Iterate over days
for day in $(seq 0 $time_period_download); do

    # ----------------------------------------------------------------------------------------
    # Get time information
    time_step=$(date -d "$time_run ${day} day ago" +'%Y-%m-%d %H:00')

    year_step=$(date -u -d "$time_step" +"%Y")
    month_step=$(date -u -d "$time_step" +"%m")
    day_step=$(date -u -d "$time_step" +"%d")
    hour_step=$(date -u -d "$time_step" +"%H")
    minute_step=$(date -u -d "$time_step" +"%M")
      
    # Define remote and local folder(s)/filename(s)
    folder_data_source_step=${folder_data_source_raw/'%Y'/$year_step}
    folder_data_source_step=${folder_data_source_step/'%m'/$month_step}
    folder_data_source_step=${folder_data_source_step/'%d'/$day_step}
    folder_data_source_step=${folder_data_source_step/'%H'/$hour_step}
    folder_data_source_step=${folder_data_source_step/'%M'/$minute_step}

    folder_data_destination_step=${folder_data_destination_raw/'%Y'/$year_step}
    folder_data_destination_step=${folder_data_destination_step/'%m'/$month_step}
    folder_data_destination_step=${folder_data_destination_step/'%d'/$day_step}
    folder_data_destination_step=${folder_data_destination_step/'%H'/$hour_step}
    folder_data_destination_step=${folder_data_destination_step/'%M'/$minute_step}

    file_data_step=${file_data_raw/'%Y'/$year_step}
    file_data_step=${file_data_step/'%m'/$month_step}
    file_data_step=${file_data_step/'%d'/$day_step}
    file_data_step=${file_data_step/'%H'/$hour_step}
    file_data_step=${file_data_step/'%M'/$minute_step}

    # Info time start
    echo " ====> TIME ${time_step} ... "

    for domain_name in "${domain_list[@]}"; do

        # Info domain start
        echo " =====> DOMAIN ${domain_name} ... "
          
        folder_data_source_domain=${folder_data_source_step/'%DOMAIN_NAME'/$domain_name}
        folder_data_destination_domain=${folder_data_destination_step/'%DOMAIN_NAME'/$domain_name}
          
        file_data_domain=${file_data_step/'%DOMAIN_NAME'/$domain_name}

        echo $folder_data_source_domain
        echo $folder_data_destination_domain

        # Create local folder
        if [ ! -d "$folder_data_destination_domain" ]; then
            mkdir -p $folder_data_destination_domain
        fi
        
        # Move file from source to destination
        echo " ======> MOVE FILE ... "
        if [ -f "${folder_data_source_domain}${file_data_domain}" ]; then
            
            echo " =======> EXECUTE: scp -r ${folder_data_source_domain}${file_data_domain} ${folder_data_destination_domain}"
            if mv ${folder_data_source_domain}${file_data_domain} ${folder_data_destination_domain}; then
                echo " ======> MOVE FILE ... DONE"
            else
                echo " ======> MOVE FILE ... FAILED. COMMAND EXITS WITH ERROR STATUS "
            fi
            
        else
            echo " ======> MOVE FILE ... FAILED. File "${folder_data_source_domain}${file_data_domain}" does not exist!"
        fi
        
        # Info domain end
        echo " =====> DOMAIN ${domain_name} ... DONE"
      
    done

    # Info time end
    echo " ====> TIME ${time_step} ... DONE"
    # ----------------------------------------------------------------------------------------
  
done
    
# Info script end
echo " ===> DOWNLOAD DYNAMIC DATA ... DONE"
echo " ==> ... END"
echo " ==> Bye, Bye"
echo " ==================================================================================="
# ----------------------------------------------------------------------------------------



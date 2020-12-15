#!/bin/bash -e

#-----------------------------------------------------------------------------------------
# Script information
script_name='ARPAL - SOILSLIP SCENARIOS - DOWNLOADER - HISTORY'
script_version="1.0.0"
script_date='2020/12/14'

# Script flag(s)
flag_download_static=false
flag_download_dynamic=true

time_period_download=75 # month(s)

# Domain list
domain_list=(
"Tanaro" "Scrivia" "Savonese" "PonenteGenovese" "Ponente" "OrbaStura" 
"Magra" "LevanteGenovese" "Imperiese" "Finalese" "Erro" "Entella" 
"CentroPonente" "Centa" "BormidaS" "BormidaM" "AvetoTrebbia"
)

# Static remote and local folder(s) 
folder_data_static_remote_raw="drift@10.24.200.114:/mnt/DatiModBil/%DOMAIN_NAMEDomain/LandData/"
folder_data_static_local_raw="/home/admin/soilslip-ws/static/basins/%DOMAIN_NAMEDomain/"
# Dynamic remote and local folder(s) 
folder_data_dynamic_remote_raw="drift@10.24.200.114:/mnt/DatiModBil/%DOMAIN_NAMEDomain/Results/Maps/"
folder_data_dynamic_local_raw="/home/admin/soilslip-ws/dynamic/source/soil_moisture/%DOMAIN_NAMEDomain/%Y/%m/"

file_data_static_raw="*"
file_data_dynamic_raw="%DOMAIN_NAMEDomainV_%Y%m*.gz"
#-----------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Get information (-u to get gmt time)
#time_run=$(date -u +"%Y-%m-%d %H:00")
time_run="2020-01-01 00:00" # DEBUG DATABASE CASE
#-----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
# Info script start
echo " ==================================================================================="
echo " ==> "$script_name" (Version: "$script_version" Release_Date: "$script_date")"
echo " ==> START ..."

# Iterate over domain and period
time_run=$(date -d "$time_run" +'%Y-%m-%d %H:00')
for domain_name in "${domain_list[@]}"; do
    
    # ----------------------------------------------------------------------------------------
    # Info domain start
    echo " ==> DOMAIN ${domain_name} ... "
    
    # Define remote and local folder(s)
    folder_data_static_remote_domain=${folder_data_static_remote_raw/'%DOMAIN_NAME'/$domain_name}
    folder_data_static_local_domain=${folder_data_static_local_raw/'%DOMAIN_NAME'/$domain_name}
    folder_data_dynamic_remote_domain=${folder_data_dynamic_remote_raw/'%DOMAIN_NAME'/$domain_name}
    folder_data_dynamic_local_domain=${folder_data_dynamic_local_raw/'%DOMAIN_NAME'/$domain_name}
    
    file_data_static_domain=${file_data_static_raw/'%DOMAIN_NAME'/$domain_name}
    file_data_dynamic_domain=${file_data_dynamic_raw/'%DOMAIN_NAME'/$domain_name}
    # ----------------------------------------------------------------------------------------
    
    # ----------------------------------------------------------------------------------------
    # Section to dowload static datasets from remote machine to local machine
    echo " ====> DOWNLOAD STATIC DATA ... "
    if $flag_download_static; then

    	# Create local folder
    	echo " =====> GET FILES ... "
	    if [ ! -d "$folder_data_static_local_domain" ]; then
		    mkdir -p $folder_data_static_local_domain
	    fi
        
        echo " =====> EXECUTE: scp -r ${folder_data_static_remote_domain}${file_data_static_domain} ${folder_data_static_local_domain}"
        
        if scp -r ${folder_data_static_remote_domain}${file_data_static_domain} ${folder_data_static_local_domain}; then
            echo " =====> GET FILES ... DONE"
        else
            echo " =====> GET FILES ... FAILED"
        fi
        
        echo " ====> DOWNLOAD STATIC DATA ... DONE"
    else
        echo " ====> DOWNLOAD STATIC DATA ... SKIPPED. NOT ACTIVATED"
    fi
    # ----------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------
    # Section to dowload static datasets from remote machine to local machine
    echo " ====> DOWNLOAD DYNAMIC DATA ... "
    if $flag_download_dynamic; then
    
        # Iterate over days
        for month in $(seq 0 $time_period_download); do
        
            # ----------------------------------------------------------------------------------------
            # Get time information
	        time_step=$(date -d "$time_run ${month} months ago" +'%Y-%m-%d %H:00')
	
	        year_step=$(date -u -d "$time_step" +"%Y")
            month_step=$(date -u -d "$time_step" +"%m")
            day_step=$(date -u -d "$time_step" +"%d")
            hour_step=$(date -u -d "$time_step" +"%H")
	        minute_step=$(date -u -d "$time_step" +"%M")
	        
	        # Info start
            echo " =====> TIME ${time_step} ... "
            
	        # Define remote and local folder(s)/filename(s)
	        folder_data_dynamic_remote_step=${folder_data_dynamic_remote_domain/'%Y'/$year_step}
            folder_data_dynamic_remote_step=${folder_data_dynamic_remote_step/'%m'/$month_step}
            folder_data_dynamic_remote_step=${folder_data_dynamic_remote_step/'%d'/$day_step}
            folder_data_dynamic_remote_step=${folder_data_dynamic_remote_step/'%H'/$hour_step}
            folder_data_dynamic_remote_step=${folder_data_dynamic_remote_step/'%M'/$minute_step}
	
	        folder_data_dynamic_local_step=${folder_data_dynamic_local_domain/'%Y'/$year_step}
            folder_data_dynamic_local_step=${folder_data_dynamic_local_step/'%m'/$month_step}
            folder_data_dynamic_local_step=${folder_data_dynamic_local_step/'%d'/$day_step}
            folder_data_dynamic_local_step=${folder_data_dynamic_local_step/'%H'/$hour_step}
            folder_data_dynamic_local_step=${folder_data_dynamic_local_step/'%M'/$minute_step}
            
	        file_data_dynamic_step=${file_data_dynamic_domain/'%Y'/$year_step}
            file_data_dynamic_step=${file_data_dynamic_step/'%m'/$month_step}
            file_data_dynamic_step=${file_data_dynamic_step/'%d'/$day_step}
            file_data_dynamic_step=${file_data_dynamic_step/'%H'/$hour_step}
            file_data_dynamic_step=${file_data_dynamic_step/'%M'/$minute_step}

        	# Create local folder
        	echo " ======> GET FILES ... "
	        if [ ! -d "$folder_data_dynamic_local_step" ]; then
		        mkdir -p $folder_data_dynamic_local_step
	        fi
            
            echo " =======> EXECUTE: scp -r ${folder_data_dynamic_remote_step}${file_data_dynamic_step} ${folder_data_dynamic_local_step}"
            if scp -r ${folder_data_dynamic_remote_step}${file_data_dynamic_step} ${folder_data_dynamic_local_step}; then
                echo " ======> GET FILES ... DONE"
            else
                 echo " ======> GET FILES ... FAILED "
            fi
            
            # Info start
            echo " =====> TIME ${time_step} ... DONE"
	        # ----------------------------------------------------------------------------------------

        done
        
        # Info download end
        echo " ====> DOWNLOAD DYNAMIC DATA ... DONE"
        # ----------------------------------------------------------------------------------------
    
    else
    
        # ----------------------------------------------------------------------------------------
        # Info download end
        echo " ====> DOWNLOAD DYNAMIC DATA ... SKIPPED. NOT ACTIVATED"
        # ----------------------------------------------------------------------------------------
        
    fi
    
    # Info domain end
    echo " ==> DOMAIN ${domain_name} ... DONE"
    # ----------------------------------------------------------------------------------------
    
done

# Info script end
echo " ==> ... END"
echo " ==> Bye, Bye"
echo " ==================================================================================="
# ----------------------------------------------------------------------------------------



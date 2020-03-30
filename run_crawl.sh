#!/bin/bash

cd $(dirname $0)

# Argumentos default
PROFILE_FILE='users.txt'
MIN_DATE=$( date --date="yesterday" +%-Y,%-m,%-d )
STORE_DAYS=2
SLEEP=0
DELETE=true
USERNAME="none"
PASSWORD="none"

function print_help {
    echo "Usage: ./run_crawl.sh -p profile_file [-d min_date] [-s archive_store_days] [-t sleep_time] [-n]" >&2 ;
    }

# fazendo parse nos argumentos da linha de comando
# args seguidos de : esperam argumentos
while getopts  "p:d:s:t:u:w:hn" flag
do
    case $flag in
        p) PROFILE_FILE=$OPTARG;;
        d) MIN_DATE=$OPTARG;;
        s) STORE_DAYS=$OPTARG;;
        t) SLEEP=$OPTARG;;
        n) DELETE=false;;
        u) USERNAME=$OPTARG;;
        w) PASSWORD=$OPTARG;;
        h) print_help; exit 2;;
        ?) print_help; exit 2;;
    esac
done

# 1 - Download Data
echo "DOWNLOADING POSTS AND PROFILES"
echo "=============================="
./1_download.sh $PROFILE_FILE $MIN_DATE $SLEEP $USERNAME $PASSWORD
echo "DOWNLOADING COMMENTS"
echo "===================="
./1_download_comments.py

# 2 - Create Archives
echo "CREATING ARCHIVES"
echo "================="
./2_create_archives.py

# 3 - Delete Staging
if ${DELETE}; then

    echo "DELETING OLD DATA"
    echo "================="
    #rm -f data/staging/*/*
    #rmdir data/staging/*

    # 4 - Remove old archives
    find data/archives/ -type d -mtime +$STORE_DAYS -printf '%p\n' | \
                        xargs -I {} -- sh -c 'echo Removing {} ; rm -f {}/*.copied ; rmdir {}'

fi

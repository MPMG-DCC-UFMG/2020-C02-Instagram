#!/bin/bash

PROFILE_FILE=$1
MIN_DATE=$2
SLEEP=$3
USERNAME=$4
PASSWORD=$5
OUTDIR="data/staging"

if [ $USERNAME == "none" ] ; then
    LOGIN=""
else
    LOGIN="--login $USERNAME --password $PASSWORD --sessionfile ./data/session"
fi

mkdir -p $OUTDIR

# Allow SIGINT to background processes
set -m

while read profile; do

    if [[ $profile == \#* ]] ; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] Skipping commented line: $profile"
    else

        echo "[$(date +'%Y-%m-%d %H:%M:%S')] Downloading $profile"

        instaloader $profile  $LOGIN    --no-pictures \
                                        --no-videos \
                                        --no-video-thumbnails \
                                        --no-captions \
                                        --post-filter="date_utc >= datetime($MIN_DATE)" \
                                        --dirname-pattern="$OUTDIR/{profile}" \
                                        > /tmp/instaloader_output_$profile 2>&1 &

        PID=$!

        while ( true ) ; do

            if ps -p $PID > /dev/null
            then
                :
            else
                break
            fi

            if grep '<skipped>' /tmp/instaloader_output_$profile 2>&1 > /dev/null
            then
                break
            else
                :
            fi

        done

        kill -INT $PID
        cat /tmp/instaloader_output_$profile
        echo -e "\n"

        sleep $SLEEP

    fi

done < $PROFILE_FILE

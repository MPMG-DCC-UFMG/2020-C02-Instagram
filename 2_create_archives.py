#!/usr/bin/python3

import datetime
import glob
import json
import time
import lzma
import os
import shutil

def now_str():
    return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")


INPUT_DIR="data/staging"
OUTPUT_DIR="data/archives"
INPUT_ARCHIVE_COMMENTS="data/staging/comments.json" #agora tá subdividido

# Create Archive Dir
TIME=datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
if not os.path.exists("data/archives/{}".format(TIME)):
    os.makedirs("data/archives/{}".format(TIME))

# cria os aquivos de saida esperados
OUTPUT_ARCHIVE_COMMENTS         ="data/archives/{}/comments.json".format(TIME)
OUTPUT_ARCHIVE_MEDIAS           ="data/archives/{}/medias.json".format(TIME)
OUTPUT_ARCHIVE_MEDIAS_PERIODIC  ="data/archives/{}/medias_periodic.json".format(TIME)
OUTPUT_ARCHIVE_PROFILES_PERIODIC="data/archives/{}/profiles_periodic.json".format(TIME)

print (now_str(), "Creating archives at:", "data/archives/{}".format(TIME))


# PROFILES AND MEDIAS
fo_medias = open(OUTPUT_ARCHIVE_MEDIAS, "w")
fo_medias_periodic = open(OUTPUT_ARCHIVE_MEDIAS_PERIODIC, "w")
fo_profiles_periodic = open(OUTPUT_ARCHIVE_PROFILES_PERIODIC, "w")


for f in glob.glob("{}/*/*.json.xz".format(INPUT_DIR)):

    try:

        if "UTC" in f:
            #abrindo os arquivos de midia para cada usuario coletado
            media = json.loads(lzma.open(f, "r").read().decode("utf-8"))
            media_code = media["node"]["shortcode"]
            print (now_str(), "Processing post:", media_code)

            # Parse media
            my_post = {}
            post = media
            my_post['id']               = post['node']['id']
            my_post['short_code']       = post['node']['shortcode']
            my_post['created_time']     = int(post['node']['taken_at_timestamp'])
            my_post['created_time_str'] = datetime.datetime.utcfromtimestamp(my_post['created_time'] ).strftime('%Y-%m-%d %H:%M:%S')
            my_post['caption']          = post['node']['edge_media_to_caption']['edges'][0]['node']['text']
            my_post['comments_count']   = post['node']['edge_media_to_comment']['count']
            my_post['likes_count']      = post['node']['edge_media_preview_like']['count']
            my_post['owner_id']         = post['node']['owner']['id']
            my_post['owner_username']   = post['node']['owner']['username']
            my_post['image_url']        = post['node']['display_url']

            if 'location' in post['node'] and post['node']['location'] is not None:
                my_post['location_id']      = post['node']['location']['id']
                my_post['location_name']    = post['node']['location']['name']
            else:
                my_post['location_id']      = None
                my_post['location_name']    = None

            my_post['dimensions']               = post['node']['dimensions']
            my_post['is_video']                 = post['node']['is_video']
            my_post['accessibility_caption']    = post['node']['accessibility_caption'] if 'accessibility_caption' in post['node'] else None
            my_post['comments_disabled']        = post['node']['comments_disabled']
            my_post['thumbnail_resources']      = post['node']['thumbnail_resources']
            my_post['__typename']               = post['node']['__typename']

            print (json.dumps(my_post), file = fo_medias)

            # Parse media
            periodic_media = {}
            periodic_media["short_code"] = my_post["short_code"]
            periodic_media["likes_count"] = my_post["likes_count"]
            periodic_media["comments_count"] = my_post["comments_count"]
            periodic_media["time_epoch"] = int(time.time())
            periodic_media["time_str"] = datetime.datetime.utcfromtimestamp(periodic_media["time_epoch"])\
                                              .strftime('%Y-%m-%d %H:%M:%S')
            print (json.dumps(periodic_media), file = fo_medias_periodic)

    except Exception as e:
        print (now_str(), "Error in file:", f, "Error:", e)

# PROFILES
for f in glob.glob("{}/*/*.json.xz".format(INPUT_DIR)):
    if not "UTC" in f:

        try:
            profile = json.loads(lzma.open(f, "r").read().decode("utf-8"))["node"]

            print (now_str(), "Processing Profile:", profile["username"])

            if 'edge_owner_to_timeline_media' in profile:
                del profile['edge_owner_to_timeline_media']
            if 'edge_felix_video_timeline' in profile:
                del profile['edge_felix_video_timeline']

            profile["time_epoch"] = int(time.time())
            profile["time_str"] = datetime.datetime.utcfromtimestamp(profile["time_epoch"])\
                                              .strftime('%Y-%m-%d %H:%M:%S')
            print (json.dumps(profile), file = fo_profiles_periodic)

        except Exception as e:
            print (now_str(), "Error in file:", f, "Error:", e)

# Copy comments
#aqui tem duas opções, copiar todos os arquivos para um só, ou só transferir os arq

try:
    folders = os.listdir(INPUT_DIR)
    folders = sorted(folders)
    n_folder = len(folders)
    final_file = open(OUTPUT_ARCHIVE_COMMENTS, "a+")
    for count in range(len(folders)):
            comment_file = INPUT_DIR+"/"+folders[count]+"/comments_"+folders[count]+".json"
            fo = open(comment_file, "r")
            #print("abriu:  ", comment_file)
            for line in fo:
                data = json.loads(line)
                print (json.dumps(data), file = final_file)
    # shutil.move(INPUT_ARCHIVE_COMMENTS, OUTPUT_ARCHIVE_COMMENTS)
except Exception as e:
    print(e)
    print (now_str(), "Error in copying comment file")

fo_medias.close()
fo_medias_periodic.close()
fo_profiles_periodic.close()

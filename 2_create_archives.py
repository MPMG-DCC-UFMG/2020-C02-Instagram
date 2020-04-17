#!/usr/bin/python3

import datetime
import glob
import json
import time
import lzma
import os
import shutil


def aggregate_comments(final_comments_file_path): # copia todos os arquivos de comentarios coletados para um arquivo so
    try:
        folders = sorted(os.listdir(INPUT_DIR))
        # folders = sorted(folders)
        n_folder = len(folders)
        final_file = open(final_comments_file_path, "a+")
        for count in range(n_folder): # pastas sao os nomes dos usuarios coletados
                comment_file_path = INPUT_DIR+"/"+folders[count]+"/comments_"+folders[count]+".json"
                comment_file = open(comment_file_path, "r")
                for line in comment_file:
                    data = json.loads(line)
                    print (json.dumps(data), file = final_file)
        # shutil.move(INPUT_ARCHIVE_COMMENTS, final_comments_file_path)
    except Exception as e:
        print(e)
        print (now_str(), "Error in copying comment file")


def aggregate_profiles(input_dir_path, outfile_profiles_periodic):
    for f in glob.glob("{}/*/*.json.xz".format(input_dir_path)):
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
                print (json.dumps(profile), file = outfile_profiles_periodic)

            except Exception as e:
                print (now_str(), "Error in file:", f, "Error:", e)

def now_str():
    return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def create_data_folder(time):
    if not os.path.exists("data/archives/{}".format(time)):
        os.makedirs("data/archives/{}".format(time))

def create_output_paths(time):
    out_comments         ="data/archives/{}/comments.json".format(TIME)
    out_medias           ="data/archives/{}/medias.json".format(TIME)
    out_medias_periodic  ="data/archives/{}/medias_periodic.json".format(TIME)
    out_profiles_periodic="data/archives/{}/profiles_periodic.json".format(TIME)
    return out_comments, out_medias, out_medias_periodic, out_profiles_periodic

def parse_archive_medias(media_file,out_medias):
    media = json.loads(lzma.open(media_file, "r").read().decode("utf-8"))
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

    print (json.dumps(my_post), file = out_medias)
    return my_post

def parse_archive_periodic_media(my_post, out_medias_periodic):
    periodic_media = {}
    periodic_media["short_code"] = my_post["short_code"]
    periodic_media["likes_count"] = my_post["likes_count"]
    periodic_media["comments_count"] = my_post["comments_count"]
    periodic_media["time_epoch"] = int(time.time())
    periodic_media["time_str"] = datetime.datetime.utcfromtimestamp(periodic_media["time_epoch"])\
                                      .strftime('%Y-%m-%d %H:%M:%S')
    print (json.dumps(periodic_media), file = out_medias_periodic)

def parse_medias(INPUT_DIR, fo_medias, fo_medias_periodic):
    for f in glob.glob("{}/*/*.json.xz".format(INPUT_DIR)):
        try:
            if "UTC" in f:
                my_post = parse_archive_medias(f,fo_medias)
                parse_archive_periodic_media(my_post, fo_medias_periodic)

        except Exception as e:
            print (now_str(), "Error in file:", f, "Error:", e)


def create_archives(INPUT_DIR, OUTPUT_DIR, INPUT_ARCHIVE_COMMENTS):
    # Cria pasta onde arquivos serão armazenados
    create_data_folder(TIME)
    # cria os aquivos de saida esperados
    OUT_ARCHIVE_COMMENTS, OUT_ARCHIVE_MEDIAS, OUT_ARCHIVE_MEDIAS_PERIODIC, OUT_ARCHIVE_PROFILES_PERIODIC = create_output_paths(TIME)

    print (now_str(), "Creating archives at:", "data/archives/{}".format(TIME))
    # perfis e midias
    fo_medias = open(OUT_ARCHIVE_MEDIAS, "w")
    fo_medias_periodic = open(OUT_ARCHIVE_MEDIAS_PERIODIC, "w")
    fo_profiles_periodic = open(OUT_ARCHIVE_PROFILES_PERIODIC, "w")

    parse_medias(INPUT_DIR, fo_medias, fo_medias_periodic)
    aggregate_profiles(INPUT_DIR, fo_profiles_periodic)
    aggregate_comments(OUT_ARCHIVE_COMMENTS)

    fo_medias.close()
    fo_medias_periodic.close()
    fo_profiles_periodic.close()


INPUT_DIR="data/staging"
OUTPUT_DIR="data/archives"
INPUT_ARCHIVE_COMMENTS="data/staging/comments.json"
TIME=datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

create_archives(INPUT_DIR, OUTPUT_DIR, INPUT_ARCHIVE_COMMENTS)

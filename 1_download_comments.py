#!/usr/bin/env python3

import json
import time
import lzma
import glob
from datetime import datetime
import timeout_decorator
import instaloader
import sys
import os

#OUTFILE="data/staging/comments.json"
MAX_COMMENTS = 100000
TIMEOUT=7200
INPUT_DIR="data/staging"

def main():
    # Go through medias
    #codes = set()
    folders = os.listdir(INPUT_DIR)
    folders = sorted(folders)
    n_folders = len(folders)
    for count in range(len(folders)):
        print("Collecting profile", (count+1),"of",n_folders,"---",folders[count])
        codes = set()
        outfile = INPUT_DIR+"/"+folders[count]+"/comments_"+folders[count]+".json"
        OUTFILE = outfile
        for f in os.listdir(INPUT_DIR+"/"+folders[count]):
            # if f.endswith("UTC.json.xz"):
            if "UTC.json.xz" in f:
                try:
                    media = json.loads(lzma.open(INPUT_DIR+"/"+folders[count]+'/'+str(f), "r").read().decode("utf-8"))
                    media_code = media["node"]["shortcode"]
                    codes.add(media_code)
                except:
                    print(f)
                    print ("Marformed json line" )

        # Crawl for each post
        fo = open(OUTFILE, "a+")
        i = instaloader.Instaloader()
        codes_list = sorted(codes)
        post_counter = 1
        #agora coleta por conta
        for code in codes_list:

            print (now_str(), "Crawling post ",post_counter, "of ", len(codes), " --- ", code)
            post_counter = post_counter + 1
            try:
                # For each comment
                n_comm = 0
                comments = get_comments_safe(i, code)
                for comment in comments:

                    my_comment = {}
                    my_comment["text"]              = comment.text
                    my_comment["created_time"]      = int(comment.created_at_utc.timestamp())
                    my_comment["created_time_str"]  = comment.created_at_utc.strftime('%Y-%m-%d %H:%M:%S')
                    my_comment["media_code"]        = code
                    my_comment["id"]                = str(comment.id)
                    my_comment["owner_username"]    = comment.owner.username
                    my_comment["owner_id"]          = str(comment.owner.userid)

                    text = my_comment['text']
                    tags =  {tag.strip("#").strip(',<.>/?;:\'"[{]}\\|=+`~!@#$%^&*()').lower() for tag in text.split() if tag.startswith("#")}
                    users = {tag.strip("@").strip(',<.>/?;:\'"[{]}\\|=+`~!@#$%^&*()').lower() for tag in text.split() if tag.startswith("@")}
                    my_comment['tags']=list(tags)
                    my_comment['mentioned_usernames']=list(users)

                    print (json.dumps(my_comment), file = fo)

                    for reply in comment.answers:
                        my_reply = {}
                        my_reply["text"]              = reply.text
                        my_reply["created_time"]      = int(reply.created_at_utc.timestamp())
                        my_reply["created_time_str"]  = reply.created_at_utc.strftime('%Y-%m-%d %H:%M:%S')
                        my_reply["media_code"]        = code
                        my_reply["id"]                = str(reply.id)
                        my_reply["owner_username"]    = reply.owner.username
                        my_reply["owner_id"]          = str(reply.owner.userid)
                        my_reply["parent_comment_id"] = str(comment.id)

                        text = my_reply['text']
                        tags =  {tag.strip("#").strip(',<.>/?;:\'"[{]}\\|=+`~!@#$%^&*()').lower() for tag in text.split() if tag.startswith("#")}
                        users = {tag.strip("@").strip(',<.>/?;:\'"[{]}\\|=+`~!@#$%^&*()').lower() for tag in text.split() if tag.startswith("@")}
                        my_reply['tags']=list(tags)
                        my_reply['mentioned_usernames']=list(users)

                        print (json.dumps(my_reply), file = fo)
                    n_comm +=1

                print (now_str(), "Crawled", n_comm, "comments")

            except timeout_decorator.TimeoutError as e:
                print (now_str(), "Timeout for post", code)
            except Exception as e:
                print (now_str(), "Error for post", code)
        fo.close()
        print("\n--- Finished Crawling comments from ",folders[count] , "---\n")

    print (now_str(), "Finish")


def now_str():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

@timeout_decorator.timeout(TIMEOUT)
def get_comments_safe(il, short_code):
    post = instaloader.Post.from_shortcode(il.context, short_code)
    n_comm = 0
    comments = []
    for c in post.get_comments():
        comments.append(c)
        n_comm +=1
        if n_comm >= MAX_COMMENTS:
            print (now_str(), "Comment limit ({}) reached".format(MAX_COMMENTS) )
            break
    return comments

main()

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

'''
Media code = codigo do post utilizado pelo instagram
'''
def now_str():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

@timeout_decorator.timeout(TIMEOUT)
def get_comments_safe(il, short_code): # retorna os comentarios dado um identificado de post (shortcode)
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

def collect_media_codes(current_profile, outfile):
    codes = set()
    # OUTFILE = outfile #refatorar: excluir outfile
    for f in os.listdir(INPUT_DIR+"/"+current_profile): # essa parte coleta os codigos identificadores do post/midia
        # if f.endswith("UTC.json.xz"):
        if "UTC.json.xz" in f:
            try:
                media = json.loads(lzma.open(INPUT_DIR+"/"+current_profile+'/'+str(f), "r").read().decode("utf-8"))
                media_code = media["node"]["shortcode"]
                codes.add(media_code)
            except:
                print(f)
                print ("Marformed json line" )

    return codes

def parse_comment(comment, outfile, media_code):
    my_comment = {}
    my_comment["text"]              = comment.text
    my_comment["created_time"]      = int(comment.created_at_utc.timestamp())
    my_comment["created_time_str"]  = comment.created_at_utc.strftime('%Y-%m-%d %H:%M:%S')
    my_comment["media_code"]        = media_code
    my_comment["id"]                = str(comment.id)
    my_comment["owner_username"]    = comment.owner.username
    my_comment["owner_id"]          = str(comment.owner.userid)

    text = my_comment['text']
    tags =  {tag.strip("#").strip(',<.>/?;:\'"[{]}\\|=+`~!@#$%^&*()').lower() for tag in text.split() if tag.startswith("#")}
    users = {tag.strip("@").strip(',<.>/?;:\'"[{]}\\|=+`~!@#$%^&*()').lower() for tag in text.split() if tag.startswith("@")}
    my_comment['tags']=list(tags)
    my_comment['mentioned_usernames']=list(users)

    print (json.dumps(my_comment), file = outfile)

def parse_comment_replies(parent_comment, reply, outfile, media_code):
    my_reply = {}
    my_reply["text"]              = reply.text
    my_reply["created_time"]      = int(reply.created_at_utc.timestamp())
    my_reply["created_time_str"]  = reply.created_at_utc.strftime('%Y-%m-%d %H:%M:%S')
    my_reply["media_code"]        = media_code
    my_reply["id"]                = str(reply.id)
    my_reply["owner_username"]    = reply.owner.username
    my_reply["owner_id"]          = str(reply.owner.userid)
    my_reply["parent_comment_id"] = str(parent_comment.id)

    text = my_reply['text']
    tags =  {tag.strip("#").strip(',<.>/?;:\'"[{]}\\|=+`~!@#$%^&*()').lower() for tag in text.split() if tag.startswith("#")}
    users = {tag.strip("@").strip(',<.>/?;:\'"[{]}\\|=+`~!@#$%^&*()').lower() for tag in text.split() if tag.startswith("@")}
    my_reply['tags']=list(tags)
    my_reply['mentioned_usernames']=list(users)

    print (json.dumps(my_reply), file = outfile)

def collect_comments(media_codes_list, outfile, iloader):
    post_counter = 1
    for code in media_codes_list:
        print (now_str(), "Crawling post ",post_counter, "of ", len(media_codes_list), " --- ", code)
        post_counter = post_counter + 1
        try:
            n_comm = 0
            comments = get_comments_safe(iloader, code) # usa o instaloader instanciado e um codigo de midia para coletar os comentarios daquele post

            for comment in comments:
                parse_comment(comment, outfile, code)
                for reply in comment.answers:
                    parse_comment_replies(comment, reply, outfile, code)
                n_comm +=1

            print (now_str(), "Crawled", n_comm, "comments")

        except timeout_decorator.TimeoutError as e: #lida com excecoes de tempo esperando p/ coleta e erro
            print (now_str(), "Timeout for post", code)
        except Exception as e:
            print (now_str(), "Error for post", code)

def main():
    folders = sorted(os.listdir(INPUT_DIR)) #as pastas tem como nome o username de cada usuario
    n_folders = len(folders)
    for count in range(n_folders):
        current_profile = folders[count]
        print("Collecting profile", (count+1),"of",n_folders,"---",current_profile)
        OUTFILE = INPUT_DIR+"/"+current_profile+"/comments_"+current_profile+".json"

        codes = collect_media_codes(current_profile,OUTFILE)

        fo = open(OUTFILE, "a+")
        iloader = instaloader.Instaloader() # refatorar trocar i para iloader
        media_codes_list = sorted(codes)

        post_counter = 1
        collect_comments(media_codes_list, fo, iloader)

        fo.close()
        print("\n--- Finished Crawling comments from ",current_profile , "---\n")

    print (now_str(), "Finished")

main()

from instaloader import Instaloader
from instaloader import Profile
import os
import datetime
import json

class Commenters():
    def __init__(self, input_file):
        self.input_file = input_file

    def _get_user_info_json(self, username):
        L = Instaloader()
        profile = Profile.from_username(L.context, username)
        profile_info = {}
        profile_info["username"] = profile.username
        profile_info["is_private"] = profile.is_private
        profile_info["mediacount"] = profile.mediacount
        profile_info["followers"] = profile.followers
        profile_info["followees"] = profile.followees
        profile_info["external_url"] = profile.external_url
        profile_info["biography"] = profile.biography
        profile_json = json.dumps(profile_info)
        return profile_json

    def _get_users_list(self, filename):
        with open(filename, "r") as f:
            data = json.loads(f.read())
        commenters = []
        for comment in data["data"]:
            try:
                commenters.append(comment["owner_username"])
            except:
                pass

        return commenters


    def aggregate_commenters(self, output_file):
        commenters_list = self._get_users_list(self.input_file)
        with open(output_file,"w") as f:
            f.write("{\"data\": [")
            for i in range(len(commenters_list)):
                commenter_info = self._get_user_info_json(commenters_list[i])
                f.write(commenter_info)
                if(i!=len(commenters_list)):
                    f.write(",")
            f.write("]}")


path = ''

cc = Commenters(path)
cc.aggregate_commenters("novasaida.json")
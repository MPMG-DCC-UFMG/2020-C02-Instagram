from instaloader import Instaloader
from instaloader import Profile
from datetime import datetime
import os
import subprocess
import time

class DownloadProfiles():
    def __init__(self, users_list,min_date,sleep, username, password):

        self._users_list = users_list
        self._tokenize_date(min_date)
        self._sleep = sleep
        self._username = username
        self._password = password
        self._out_dir = "data/staging"
        subprocess.run(["mkdir" ,"-p" , self._out_dir])

        self._iloader = Instaloader(download_comments=False,download_pictures=False, 
                    download_geotags=False, download_videos=False)
        
        self._iloader.login(self._username,self._password)
        self._iloader.save_session_to_file("./data/session")


    def _tokenize_date(self, date_str):
        date_list = date_str.split(",")
        self._year = int(date_list[0])
        self._month = int(date_list[1])
        self._day = int(date_list[2])
       

    def download_profiles(self):
        """
        
        Parâmetros
        -----------
            Nenhum
        """
        for user in self._users_list:
            prof = set()
            prof.add(Profile.from_username(self._iloader.context, user))
            subprocess.run(["mkdir","-p",str(self._out_dir+"/"+user)])
            self._iloader.dirname_pattern = self._out_dir + "/" + str(user)
            self._iloader.download_profiles(prof, 
                                post_filter=lambda post: post.date_utc >= datetime(self._year,self._month,self._day))
            
            time.sleep(self._sleep)



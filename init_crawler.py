import sys
import json
import os
from download_medias import download_medias as dm

USERS_FILENAME = "users.txt"


# def get_input_json():
#     try:
#         input_json = sys.argv[1]
#         print("Name of input file: ", input_json)
#     except:
#         print("No input file provided. Exiting program...")
#         quit()
#     return input_json


# def create_users_input_file(input_json_data, aux_users_filename):
#     users_list = input_json_data["users"]
#     with open(aux_users_filename, "w") as f:
#         for user in users_list:
#             f.write(user+"\n")


# def init_comandline_crawler(sleep_time, min_date, aux_users_filename):
#     command = "./run_crawl.sh -p " + \
#         str(aux_users_filename)+" -d " + str(min_date)
#     if(sleep_time is not None):
#         command = command + " -t " + str(sleep_time)

#     os.system(command)


# def parse_json(input_json):
#     with open(input_json, "r") as f:
#         input_json_data = json.load(f)

#     sleep_time = input_json_data["sleep_time"]
#     min_date = input_json_data["min_date"]
#     create_users_input_file(input_json_data, USERS_FILENAME)
#     init_comandline_crawler(sleep_time, min_date, USERS_FILENAME)
#     os.remove(USERS_FILENAME)


# def download_medias(input_json):
#     print("======================")
#     print("DOWNLOADING MEDIAS")
#     print("======================")
#     download_photo = dm(input_json)
#     download_photo.download(verbose=True)


# input_json = get_input_json()
# parse_json(input_json)
# download_medias(input_json)
# ./run_crawl.sh -p aux.txt -d "2020,4,25"


class Coletor():
    def __init__(self):
        self.input_json = self._get_input_json()

    def _get_input_json(self):
        try:
            input_json = sys.argv[1]
            print("Name of input file: ", input_json)
        except:
            print("No input file provided. Exiting program...")
            quit()
        return input_json

    def _create_users_input_file(self, input_json_data, aux_users_filename):
        users_list = input_json_data["users"]
        with open(aux_users_filename, "w") as f:
            for user in users_list:
                f.write(user+"\n")

    def _init_comandline_crawler(self, sleep_time, min_date, aux_users_filename):
        command = "./run_crawl.sh -p " + \
            str(aux_users_filename)+" -d " + str(min_date)
        if(sleep_time is not None):
            command = command + " -t " + str(sleep_time)

        os.system(command)

    def _parse_json(self):
        with open(self.input_json, "r") as f:
            input_json_data = json.load(f)

        sleep_time = input_json_data["sleep_time"]
        min_date = input_json_data["min_date"]
        self._create_users_input_file(input_json_data, USERS_FILENAME)
        self._init_comandline_crawler(sleep_time, min_date, USERS_FILENAME)
        os.remove(USERS_FILENAME)

    def _download_medias(self):
        print("==============================")
        print("DOWNLOADING MEDIAS")
        print("==============================")
        download_photo = dm(self.input_json)
        download_photo.download(verbose=True)

    def init_crawler(self):
        self._parse_json()
        self._download_medias()


c = Coletor()
c.init_crawler()

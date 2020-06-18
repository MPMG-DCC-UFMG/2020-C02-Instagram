from instaloader import Profile
from instaloader import Instaloader
import sys
import os
import json

# input_json = sys.argv[1]
# with open(self.input_json, "r") as f:
#             input_json_data = json.load(f)
# users_list = input_json_data["users_to_download_followers"]
# followers_max = input_json_data["followers_max"]

# L = Instaloader()
# L.login(user="testejohndoe",passwd="senhasenha")
# profile = Profile.from_username(L.context, USERNAME)
# for follower in profile.get_followers():
#     print(follower.username)

class DownloadFollowers(object):
    def __init__(self, filename):
        """
        Inicia o objeto.

        Parâmetros
        -----------
            Nenhum
        """
        self.input_json_data = self._get_input_json(filename)
        self.users_list = self._get_users_list()
        self.followers_max = self._get_followers_max()
        self.credentials = {}
        self.credentials["user"] = self._get_user()
        self.credentials["passwd"] = self._get_passwd()
        self.path = self._get_path()

    def _get_input_json(self, filename):
        """
        Retorna o nome do arquivo .json que será lido via linha de comando

        Parâmetros
        -----------
            Nenhum
        """
        try:
            input_json = filename
            with open(input_json, "r") as f:
                input_json_data = json.load(f)
        except Exception as e:
            print(e)
            print("No input file provided. Exiting program...")
            quit()

        return input_json_data
    
    def _get_users_list(self):
        users_list = self.input_json_data["users_to_download_followers"]
        return users_list

    def _get_followers_max(self):
        followers_max = self.input_json_data["followers_max"]
        return followers_max

    def _get_user(self):
        return self.input_json_data["user"]

    def _get_passwd(self):
        return self.input_json_data["passwd"]


    def _get_path(self):
        """
        Guarda o nome do diretório destino das mídias.
        Verifica se foi especificado ou se devemos usar a pasta
        padrão do Instagram.
        """
        folder = str(max([int(x) for x in os.listdir("data/archives")
            if x != 'staging' and x[0] != '.']))

        if not os.path.exists("data/archives/"+folder+'/followers'):
            os.makedirs("data/archives/"+folder+'/followers')
        path = "data/archives/"+folder+'/followers/'
        return path

    def download_followers(self):
        L = Instaloader()
        try:
            L.login(user=self.credentials["user"],passwd=self.credentials["passwd"])
            
            for user in self.users_list:
                
                profile = Profile.from_username(L.context, user)
                if self.followers_max == None: #se nao for dado valor maximo, coleta todos os seguidores
                    self.followers_max = profile.followers
                print("Downloading "+str(self.followers_max)+" followers of: ", user)
                with open(self.path+"followers_"+str(user)+".txt", "w") as f:
                    counter = 0
                    for follower in profile.get_followers():
                        if counter == self.followers_max:
                            break
                        # print(follower.username)s
                        f.write(follower.username +"\n")
                        counter = counter + 1
        except Exception as e:
            print(e)

# followers = DownloadFollowers("input/novacoleta.json")
# followers.download_followers()
from instaloader import Profile
from instaloader import Instaloader
import sys
import os
import json

class DownloadFollowers():
    """
    Classe para realizar o download de seguidores de uma lista
    de perfis especificada

    Atributos
    ---------
    input_json_data : dict
        Dicionário que armazena o .json de entrada
    users_list : list
        Lista de usuários que devem ter sua lista de seguidores coletadas
    followers_max : int
        Número máximo de seguidores que devem ser baixados por perfil
    credentials : dict
        Dicionário que armazena nome de usuário e senha do conta ativa
        do instagram necessária para realizar a coleta de seguidores
    path : str
        Caminho para a pasta onde serão armazenados os arquivos com a lista de seguidores

    Métodos
    -------
    download_followers()
        Itera sobre a lista de perfis que devem ter a lista de seguidores baixada,
        realiza o download e armazena na pasta da coleta.
    """
    def __init__(self, Json):
        """
        Inicia o objeto.

        Parâmetros
        -----------
            filename : str
                nome do arquivo de entrada json
        """
        self.input_json_data = Json
        self.users_list = self._get_users_list()
        self.followers_max = self._get_followers_max()
        self.credentials = {}
        self.credentials["user"] = self._get_user()
        self.credentials["passwd"] = self._get_passwd()
        self.path = self._get_path()

    def _get_users_list(self):
        """
        Le a lista de perfis que devem ter a lista de seguidores baixada
        """
        users_list = self.input_json_data["users_to_download_followers"]
        return users_list

    def _get_followers_max(self):
        """
        Le o numero maximo de seguidores que devem ser lidos de cada perfil
        """
        followers_max = self.input_json_data["followers_max"]
        return followers_max

    def _get_user(self):
        """
        Le o nome de usuario da conta necessaria para fazer credenciamento
        necessario para baixar os seguidores
        """
        return self.input_json_data["user"]

    def _get_passwd(self):
        """
        Le a senha da conta necessaria para fazer credenciamento
        necessario para baixar os seguidores
        """
        return self.input_json_data["passwd"]


    def _get_path(self):
        """
        Guarda o nome do diretório destino das mídias.
        Verifica se foi especificado ou se devemos usar a pasta
        padrão do Instagram.
        """
        folder = str(max([int(x) for x in os.listdir("data/archives")
            if x != 'staging' and x[0] != '.']))

        path = "data/archives/"+folder+'/staging/'
        return path

    def download_followers(self):
        """
        Itera sobre a lista de perfis que devem ter a lista de seguidores baixada,
        realiza o download e armazena na pasta da coleta.
        """
        L = Instaloader()
        try:
            L.login(user=self.credentials["user"],passwd=self.credentials["passwd"])
            
            for user in self.users_list:
                
                profile = Profile.from_username(L.context, user)
                if self.followers_max == None: #se nao for dado valor maximo, coleta todos os seguidores
                    self.followers_max = profile.followers
                print("Downloading "+str(self.followers_max)+" followers of: ", user)
                with open(self.path+str(user)+"/followers_"+str(user)+".json", "w") as f:
                    counter = 0
                    for follower in profile.get_followers():
                        if counter == self.followers_max:
                            break

                        f.write("{\"usuario\":\""+str(user)+"\",\"follower\":\""+str(follower.username) +"\"}\n")
                        counter = counter + 1
        except Exception as e:
            print(e)

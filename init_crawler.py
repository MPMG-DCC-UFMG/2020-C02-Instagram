import sys
import json
import os
import subprocess
import argparse
import json_flatten as jf
from download_medias import download_medias as dm
from followers import DownloadFollowers as df
from hashtags import DownloadHashtags as dh
from profiles import DownloadProfiles as dp
from comments import DownloadComments as dc
from create_archives import CreateArchives as ca
from commenters import Commenters
from utils import extract_files as ef

# USERS_FILENAME = "users.txt" # nao alterar
# MAX_COMMENT_FILE = "max_comment_file.txt" # nao alterar

class Coletor():
    """
    Classe para inicializar o coletor. Realiza a leitura da entrada via
    argumento de linha de comando, e passa para os módulos que coletam 
    as informações de cada perfil, assim como o download das mídias dos
    perfis selecionados. 

    Atributos
    -----------
    input_json : str
        Nome do arquivo .json lido como entrada via linha de comando

    Métodos
    -----------
    init_crawler()
        Função que inicializa o crawler, lendo o arquivo .json de entrada
        e fazendo a chamada das funções que inicializam a coleta dos perfis
        e das mídias.

    """

    def __init__(self):
        """
        Inicia o objeto.

        Parâmetros
        -----------
            Nenhum
        """
        self._get_input_json()

    def _get_input_json(self):
        """
        Salva no objeto o arquivo .json de entrada.

        Parâmetros
        -----------
            Nenhum
        """
        try:
            cmd = sys.argv[1]
        except:
            print("No input provided. Exiting program...")
            quit()

        if cmd == "--json":
            try:
                data = sys.argv[2]
                with open(data, "r") as f:
                    self.input_json = json.load(f)
                print("Input mode: JSON file")
            except:
                print("No input file provided. Exiting program...")
                quit()

        else:
            data = cmd.replace("'", '"')
            self.input_json = json.loads(data)
            print("Input mode: JSON string")


    def _create_max_comments_input_file(self, max_comment_file):
        with open(max_comment_file, "w") as f:
            # print(str(input_json_data["max_comments"]))
            f.write(str(self.input_json["max_comments"]))

    def _create_users_input_file(self, aux_users_filename):
        """
        Cria um arquivo temporário que armazena os nomes dos perfis que
        devem ser coletados, um por linha. Este arquivo facilita o 
        funcionamento do coletor, pois é mais facilmente interpretado 
        pelo script "1_download.sh" 
        
        Parâmetros
        -----------
            aux_users_filename: str
                nome do arquivo temporário que será criado
        """
        users_list = self.input_json["users"]
        with open(aux_users_filename, "w") as f:
            for user in users_list:
                f.write(user+"\n")


    def _move_staging_files(self):
        #### coleta a lista de pastas dentro de archives
        result = subprocess.run(["ls","--sort=version","-r", "data/archives/"], stdout=subprocess.PIPE)
        files_list= result.stdout.decode('utf-8')
        files_list = files_list.split('\n')
        
        final_file_path = "data/archives/"+files_list[0]
        
        subprocess.run(["mv","data/staging",final_file_path])

    ####### TROCAR O NOME DO METODO
    def _init_comandline_crawler(self, sleep_time, max_comments,  min_date, users_list, username, password):
        """
        Cria a string do comando para terminal que inicializa o coletor de perfis
        e posts. Como o parâmetro sleep_time é opcional, o adiciona quando necessário
        
        Parâmetros
        -----------
        sleep_time : int
            tempo de espera entre a coleta de dois perfis
        min_date: str
            data a partir da qual devem ser coletados os posts de cada perfil
        aux_users_filename: str
            nome do arquivo temporário criado com os nomes dos perfis que serão coletados
        """
        # command = "./run_crawl.sh -p " + \
        #     str(aux_users_filename)+" -d " + str(min_date) \
        #     + " -u " + str(username) + " -w " + str(password)
        # if(sleep_time is not None):
        #     command = command + " -t " + str(sleep_time)

        # print(command)
        # os.system(command)
        dprofiles = dp(users_list,min_date,sleep_time,username,password)
        dprofiles.download_profiles()

        dcomments = dc(max_comments, "data/staging")
        dcomments.download_comments()

        carchives = ca("data/staging", "data/archives", "data/staging/comments.json")
        carchives.create_archives()


        self._move_staging_files()

    def _parse_json(self):
        """
        Realiza o parsing do .json de entrada, cria e deleta
        o arquivo temporário com os perfis que devem ser coletados, e 
        inicializa a coleta dos perfis e posts via linha de comando

        Parâmetros
        -----------
            Nenhum 
        """
        sleep_time = self.input_json["sleep_time"]
        min_date = self.input_json["min_date"]
        username = self.input_json["user"]
        password = self.input_json["passwd"]
        users_list = self.input_json["users"]
        max_comments = self.input_json["max_comments"]
        # self._create_users_input_file(USERS_FILENAME)
        # self._create_max_comments_input_file(MAX_COMMENT_FILE)
        self._init_comandline_crawler(sleep_time, max_comments,min_date, users_list, username, password)
        # os.remove(USERS_FILENAME)
        # os.remove(MAX_COMMENT_FILE)

    def _download_medias(self):
        print("==============================")
        print("DOWNLOADING MEDIAS")
        print("==============================")
        download_photo = dm(self.input_json)
        download_photo.download(verbose=True)

    def _arrange(self):
        print("==============================")
        print("MOVING POSTS")
        print("==============================")

        folder = "data/archives/"
        folder += str(max([int(x) for x in os.listdir(folder)
            if x != 'staging' and x[0] != '.']))
        folder += "/staging/"
        for profile in os.listdir(folder):
            n = len(profile)
            output = folder + profile + '/posts/'
            if not os.path.exists(output):
                os.makedirs(output)
            for post in os.listdir(folder + profile):
                name = folder+profile+"/"+post
                if post[:n] == profile:
                    if post[-3:] != "jpg":
                        os.rename(name, folder+profile+"/perfil_"+post)
                    else:
                        print("AAAAAAAAAA",post,folder+profile+"/"+post[len(profile)+1:])
                        os.rename(name, folder+profile+"/"+post[len(profile)+1:])
                elif post[-3:] != "jpg" \
                    and post[:8] != "comments" \
                    and not os.path.isdir(name) \
                    and post != "id" \
                    and post[:9] != "followers":
                    os.rename(name, output+post)

    def _select_post(self, j):
        j = j["node"]
        campos = {
            "id_post": j["id"],
            "codigo_de_media": j["shortcode"],
            "mensagem": \
                j["edge_media_to_caption"]["edges"][0]["node"]["text"],
            "publicado_em": j["taken_at_timestamp"],
            "display_url": j["display_url"],
            "eh_video": j["is_video"],
            "legenda_de_acessibilidade": j["accessibility_caption"],
            "comentarios_desativados": j["comments_disabled"],
            "numero_de_comentarios": j["edge_media_to_comment"]["count"],
            "numero_de_likes": j["edge_liked_by"]["count"],
            "localizacao_post": j["location"]
        }

        if campos["localizacao_post"] == "":
            campos["localizacao_post"] = None

        if campos["localizacao_post"] is not None:
            campos["localizacao_post"] = \
                campos["localizacao_post"]["name"]

        return campos

    def _select_perfil(self, j):
        j = j["node"]
        try:
            localizacao = j["iphone_struct"]["city_name"]
        except:
            localizacao = None
        campos = {
            "id_do_perfil": j["id"],
            "usuario": j["username"],
            "nome_completo": j["full_name"],
            "biografia": j["biography"],
            "url_externa": j["external_url"],
            "numero_de_seguidores": j["edge_followed_by"]["count"],
            "numero_de_perfis_seguidos": j["edge_follow"]["count"],
            "eh_conta_comercial": j["is_business_account"],
            "eh_conta_privada": j["is_private"],
            "eh_conta_verificada": j["is_verified"],
            "localizacao": localizacao
        }
        return campos

    def _select(self):
        print("==============================")
        print("CLEANING JSON")
        print("==============================")
    
        folder = "data/archives/"
        folder += str(max([int(x) for x in os.listdir(folder)
            if x != 'staging' and x[0] != '.']))
        
        if self.input_json["download_hashtags"]:
            folder += "/hashtags/"
            files = set()
            for tag in os.listdir(folder):
                for post in os.listdir(folder + tag):
                    if post[-5:] == ".json":
                        files.add(folder+tag+"/"+post)

            for filename in files:
                with open(filename, "r") as f:
                    j = json.load(f)
                j = self._select_post(j)
                with open(filename, "w") as f:
                    json.dump(j, f, ensure_ascii=False)
                
        else:
            folder += "/staging/"
            profiles = set()
            posts = set()
            for profile in os.listdir(folder):
                for perfil in os.listdir(folder + profile):
                    if perfil[:6] == "perfil":
                        profiles.add(folder+profile+"/"+perfil)
                for post in os.listdir(folder + profile + "/posts/"):
                    if post[-5:] == ".json":
                        posts.add(folder+profile+"/posts/"+post)

            for filename in posts:
                with open(filename, "r") as f:
                    j = json.load(f)
                j = self._select_post(j)
                with open(filename, "w") as f:
                    json.dump(j, f, ensure_ascii=False)

            for filename in profiles:
                with open(filename, "r") as f:
                    j = json.load(f)
                j = self._select_perfil(j)
                with open(filename, "w") as f:
                    json.dump(j, f, ensure_ascii=False)


    def _download_followers(self):
        print("==============================")
        print("DOWNLOADING FOLLOWERS")
        print("==============================")
        dfollowers = df(self.input_json)
        dfollowers.download_followers()

    def _download_hashtags(self):
        dhashtags = dh(self.input_json)
        dhashtags.download_hashtags()

    def _download_commenters(self, username_login, password):
        print("==============================")
        print("DOWNLOADING COMMENTERS")
        print("==============================")
        cc = Commenters()
        cc.aggregate_commenters(username_login, password)

    def init_crawler(self):
        """
        Inicializa a coleta de perfis, posts e mídias, ou de hashtags.

        Parâmetros
        -----------
            Nenhum
        """
        if (self.input_json["download_hashtags"]):
            self._download_hashtags()
        else:
            self._parse_json()
            self._download_followers()
            try:
                username = self.input_json["user"]
                password = self.input_json["passwd"]
                self._download_commenters(username,password)
            except Exception as e:
                print("Nao foi possivel coletar todos os commenters...")
                print(e)
                pass
            self._arrange()

        ef("data")
        
        if not (self.input_json["download_hashtags"]):
            self._download_medias()

        self._select()

c = Coletor()
c.init_crawler()

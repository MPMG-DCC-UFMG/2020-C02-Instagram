#!/usr/bin/python3

import datetime
import glob
import json
import time
import lzma
import os
import shutil


# # copia todos os arquivos de comentarios coletados para um arquivo so
# def aggregate_comments(final_comments_file_path):
#     try:
#         folders = sorted(os.listdir(INPUT_DIR))
#         n_folder = len(folders)
#         final_file = open(final_comments_file_path, "a+")
#         # Transformando em um json so, ao contrario de 1 por linha
#         print("{\"data\": [", file=final_file)
#         for count in range(n_folder):  # pastas sao os nomes dos usuarios coletados
#             comment_file_path = INPUT_DIR+"/" + \
#                 folders[count]+"/comments_"+folders[count]+".json"
#             comment_file = open(comment_file_path, "r")
#             for line in comment_file:
#                 data = json.loads(line)
#                 print(json.dumps(data) + ",", file=final_file)
#         print("{}]}", file=final_file)
#         # shutil.move(INPUT_ARCHIVE_COMMENTS, final_comments_file_path)
#     except Exception as e:
#         print(e)
#         print(now_str(), "Error in copying comment file")


# def aggregate_profiles(input_dir_path, outfile_profiles_periodic):
#     # Transformando em um json so, ao inves de um por linha
#     print("{\"data\": [", file=outfile_profiles_periodic)
#     # percorre os arquivos com informacoes sobre os perfis coletados
#     for f in glob.glob("{}/*/*.json.xz".format(input_dir_path)):
#         if not "UTC" in f:
#             try:
#                 profile = json.loads(
#                     lzma.open(f, "r").read().decode("utf-8"))["node"]

#                 print(now_str(), "Processing Profile:", profile["username"])

#                 if 'edge_owner_to_timeline_media' in profile:
#                     del profile['edge_owner_to_timeline_media']
#                 if 'edge_felix_video_timeline' in profile:
#                     del profile['edge_felix_video_timeline']

#                 profile["time_epoch"] = int(time.time())
#                 profile["time_str"] = datetime.datetime.utcfromtimestamp(profile["time_epoch"])\
#                     .strftime('%Y-%m-%d %H:%M:%S')
#                 print(json.dumps(profile) + ",",
#                       file=outfile_profiles_periodic)

#             except Exception as e:
#                 print(now_str(), "Error in file:", f, "Error:", e)
#     print("{}]}", file=outfile_profiles_periodic)


# def now_str():
#     return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")


# def create_data_folder(time):
#     if not os.path.exists("data/archives/{}".format(time)):
#         os.makedirs("data/archives/{}".format(time))


# def create_output_paths(time):
#     out_comments = "data/archives/{}/comments.json".format(TIME)
#     out_medias = "data/archives/{}/medias.json".format(TIME)
#     out_medias_periodic = "data/archives/{}/medias_periodic.json".format(TIME)
#     out_profiles_periodic = "data/archives/{}/profiles_periodic.json".format(
#         TIME)
#     return out_comments, out_medias, out_medias_periodic, out_profiles_periodic


# def parse_archive_medias(media_file, out_medias):
#     media = json.loads(lzma.open(media_file, "r").read().decode("utf-8"))
#     media_code = media["node"]["shortcode"]
#     print(now_str(), "Processing post:", media_code)

#     # Parse media
#     my_post = {}
#     post = media
#     my_post['id'] = post['node']['id']
#     my_post['short_code'] = post['node']['shortcode']
#     my_post['created_time'] = int(post['node']['taken_at_timestamp'])
#     my_post['created_time_str'] = datetime.datetime.utcfromtimestamp(
#         my_post['created_time']).strftime('%Y-%m-%d %H:%M:%S')
#     my_post['caption'] = post['node']['edge_media_to_caption']['edges'][0]['node']['text']
#     my_post['comments_count'] = post['node']['edge_media_to_comment']['count']
#     my_post['likes_count'] = post['node']['edge_media_preview_like']['count']
#     my_post['owner_id'] = post['node']['owner']['id']
#     my_post['owner_username'] = post['node']['owner']['username']
#     my_post['image_url'] = post['node']['display_url']

#     if 'location' in post['node'] and post['node']['location'] is not None:
#         my_post['location_id'] = post['node']['location']['id']
#         my_post['location_name'] = post['node']['location']['name']
#     else:
#         my_post['location_id'] = None
#         my_post['location_name'] = None

#     my_post['dimensions'] = post['node']['dimensions']
#     my_post['is_video'] = post['node']['is_video']
#     my_post['accessibility_caption'] = post['node']['accessibility_caption'] if 'accessibility_caption' in post['node'] else None
#     my_post['comments_disabled'] = post['node']['comments_disabled']
#     my_post['thumbnail_resources'] = post['node']['thumbnail_resources']
#     my_post['__typename'] = post['node']['__typename']

#     print(json.dumps(my_post)+",", file=out_medias)
#     return my_post


# def parse_archive_periodic_media(my_post, out_medias_periodic):
#     periodic_media = {}
#     periodic_media["short_code"] = my_post["short_code"]
#     periodic_media["likes_count"] = my_post["likes_count"]
#     periodic_media["comments_count"] = my_post["comments_count"]
#     periodic_media["time_epoch"] = int(time.time())
#     periodic_media["time_str"] = datetime.datetime.utcfromtimestamp(periodic_media["time_epoch"])\
#         .strftime('%Y-%m-%d %H:%M:%S')
#     print(json.dumps(periodic_media) + ",", file=out_medias_periodic)


# def parse_medias(INPUT_DIR, fo_medias, fo_medias_periodic):
#     print("{\"data\": [", file=fo_medias)
#     print("{\"data\": [", file=fo_medias_periodic)
#     for f in glob.glob("{}/*/*.json.xz".format(INPUT_DIR)):
#         try:
#             if "UTC" in f:
#                 my_post = parse_archive_medias(f, fo_medias)
#                 parse_archive_periodic_media(my_post, fo_medias_periodic)

#         except Exception as e:
#             print(now_str(), "Error in file:", f, "Error:", e)
#     print("{}]}", file=fo_medias)
#     print("{}]}", file=fo_medias_periodic)


# def create_archives(INPUT_DIR, OUTPUT_DIR, INPUT_ARCHIVE_COMMENTS):
#     # Cria pasta onde arquivos serão armazenados
#     create_data_folder(TIME)
#     # cria os aquivos de saida esperados
#     OUT_ARCHIVE_COMMENTS, OUT_ARCHIVE_MEDIAS, OUT_ARCHIVE_MEDIAS_PERIODIC, OUT_ARCHIVE_PROFILES_PERIODIC = create_output_paths(
#         TIME)

#     print(now_str(), "Creating archives at:", "data/archives/{}".format(TIME))
#     # perfis e midias
#     fo_medias = open(OUT_ARCHIVE_MEDIAS, "w")
#     fo_medias_periodic = open(OUT_ARCHIVE_MEDIAS_PERIODIC, "w")
#     fo_profiles_periodic = open(OUT_ARCHIVE_PROFILES_PERIODIC, "w")

#     parse_medias(INPUT_DIR, fo_medias, fo_medias_periodic)
#     aggregate_profiles(INPUT_DIR, fo_profiles_periodic)
#     aggregate_comments(OUT_ARCHIVE_COMMENTS)

#     fo_medias.close()
#     fo_medias_periodic.close()
#     fo_profiles_periodic.close()


# INPUT_DIR = "data/staging"
# OUTPUT_DIR = "data/archives"
# INPUT_ARCHIVE_COMMENTS = "data/staging/comments.json"
# TIME = int(datetime.datetime.now().replace(microsecond=0).timestamp())
# # TIME = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") versao antiga
# create_archives(INPUT_DIR, OUTPUT_DIR, INPUT_ARCHIVE_COMMENTS)


class CreateArchives():
    """
    Classe que cria arquivos e pastas que irão compilar informações
    de mídias, perfis, posts e comentários coletados pelo Instaloader 

    Atributos
    ---------
    INPUT_DIR : str
        nome da pasta onde são armazenados os arquivos de entrada
    OUTPUT_DIR : str
        nome da pasta onde serão armazenados os arquivos de saída
    INPUT_ARCHIVE_COMMENTS : str
        nome do arquivo que irá compilar os comentários de todos os posts
    TIME : str
        timestamp utilizada para identificar cada pasta de coleta
        

    Métodos
    ---------
    create_archives()
        Função que cria os arquivos e pastas de saída, organizando
        os arquivos de saída gerados pela coleta de perfis, posts 
        e comentários
    """
    def __init__(self, INPUT_DIR, OUTPUT_DIR, INPUT_ARCHIVE_COMMENTS):
        """
        Inicializa o objeto

        Parâmetros
        ---------
        INPUT_DIR : str
            nome da pasta onde são armazenados os arquivos de entrada
        OUTPUT_DIR : str
            nome da pasta onde serão armazenados os arquivos de saída
        INPUT_ARCHIVE_COMMENTS : str
            nome do arquivo que irá compilar os comentários de todos os posts
        TIME : str
            timestamp utilizada para identificar cada pasta de coleta
        
        """
        self.INPUT_DIR = INPUT_DIR
        self.OUTPUT_DIR = OUTPUT_DIR
        self.INPUT_ARCHIVE_COMMENTS = INPUT_ARCHIVE_COMMENTS
        self.TIME = int(datetime.datetime.now().replace(
            microsecond=0).timestamp())

    def _aggregate_comments(self, final_comments_file_path):
        """
        Agrega todos os comentários coletados em um arquivo só.
        Gera um .json de saída

        Parâmetros
        ---------
        final_comments_file_path : str
            nome do arquivo de saida que compila os comentários
        """
        # copia todos os arquivos de comentarios coletados para um arquivo so
        try:
            folders = sorted(os.listdir(self.INPUT_DIR))
            n_folder = len(folders)
            final_file = open(final_comments_file_path, "a+")
            # Transformando em um json so, ao contrario de 1 por linha
            print("{\"data\": [", file=final_file)
            for count in range(n_folder):  # pastas sao os nomes dos usuarios coletados
                comment_file_path = self.INPUT_DIR+"/" + \
                    folders[count]+"/comments_"+folders[count]+".json"
                comment_file = open(comment_file_path, "r")
                for line in comment_file:
                    data = json.loads(line)
                    print(json.dumps(data) + ",", file=final_file)
            print("{}]}", file=final_file)
            # shutil.move(INPUT_ARCHIVE_COMMENTS, final_comments_file_path)
        except Exception as e:
            print(e)
            print(self._now_str(), "Error in copying comment file")

    def _aggregate_profiles(self, outfile_profiles_periodic):
        """
        Agrega as informações de perfis em um único .json de saída

        Parâmetros
        ---------
        outfile_profiles_periodic : file 
            arquivo de saída que armazena as informações sobre os perfis
            coletados 
        """
        # Transformando em um json so, ao inves de um por linha
        print("{\"data\": [", file=outfile_profiles_periodic)
        # percorre os arquivos com informacoes sobre os perfis coletados
        for f in glob.glob("{}/*/*.json.xz".format(self.INPUT_DIR)):
            if not "UTC" in f:
                try:
                    profile = json.loads(
                        lzma.open(f, "r").read().decode("utf-8"))["node"]

                    print(self._now_str(), "Processing Profile:",
                          profile["username"])

                    if 'edge_owner_to_timeline_media' in profile:
                        del profile['edge_owner_to_timeline_media']
                    if 'edge_felix_video_timeline' in profile:
                        del profile['edge_felix_video_timeline']

                    profile["time_epoch"] = int(time.time())
                    profile["time_str"] = datetime.datetime.utcfromtimestamp(profile["time_epoch"])\
                        .strftime('%Y-%m-%d %H:%M:%S')
                    print(json.dumps(profile) + ",",
                          file=outfile_profiles_periodic)

                except Exception as e:
                    print(self._now_str(), "Error in file:", f, "Error:", e)
        print("{}]}", file=outfile_profiles_periodic)

    def _now_str(self):
        """
        Retorna um timestamp do momento em que a função é chamada
        """
        return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

    def _create_data_folder(self):
        """
        Cria pasta onde serão armazenados os arquivos da coleta atual.
        O nome da pasta será o timestamp de sua criação
        """
        if not os.path.exists("data/archives/{}".format(self.TIME)):
            os.makedirs("data/archives/{}".format(self.TIME))

    def _create_output_paths(self):
        """
        Cria os arquivos de saída de comentários, mídias e perfis.
        """
        out_comments = "data/archives/{}/comments.json".format(self.TIME)
        out_medias = "data/archives/{}/medias.json".format(self.TIME)
        out_medias_periodic = "data/archives/{}/medias_periodic.json".format(
            self.TIME)
        out_profiles_periodic = "data/archives/{}/profiles_periodic.json".format(
            self.TIME)
        return out_comments, out_medias, out_medias_periodic, out_profiles_periodic

    def _parse_archive_medias(self, media_file, out_medias):
        """
        Recebe um arquivo de post/mídias, realiza parsing
        e escreve em um arquivo de saída

        Parâmetros
        ----------
        media : str
            nome de um arquivo de mídia/post que será processado
        out_medias : file
            arquivo que ira compilar as informações de todas 
            as mídias/posts coletadas
        """
        media = json.loads(lzma.open(media_file, "r").read().decode("utf-8"))
        media_code = media["node"]["shortcode"]
        print(self._now_str(), "Processing post:", media_code)

        # Parse media
        my_post = {}
        post = media
        my_post['id'] = post['node']['id']
        my_post['short_code'] = post['node']['shortcode']
        my_post['created_time'] = int(post['node']['taken_at_timestamp'])
        my_post['created_time_str'] = datetime.datetime.utcfromtimestamp(
            my_post['created_time']).strftime('%Y-%m-%d %H:%M:%S')
        my_post['caption'] = post['node']['edge_media_to_caption']['edges'][0]['node']['text']
        my_post['comments_count'] = post['node']['edge_media_to_comment']['count']
        my_post['likes_count'] = post['node']['edge_media_preview_like']['count']
        my_post['owner_id'] = post['node']['owner']['id']
        my_post['owner_username'] = post['node']['owner']['username']
        my_post['image_url'] = post['node']['display_url']

        if 'location' in post['node'] and post['node']['location'] is not None:
            my_post['location_id'] = post['node']['location']['id']
            my_post['location_name'] = post['node']['location']['name']
        else:
            my_post['location_id'] = None
            my_post['location_name'] = None

        my_post['dimensions'] = post['node']['dimensions']
        my_post['is_video'] = post['node']['is_video']
        my_post['accessibility_caption'] = post['node']['accessibility_caption'] if 'accessibility_caption' in post['node'] else None
        my_post['comments_disabled'] = post['node']['comments_disabled']
        my_post['thumbnail_resources'] = post['node']['thumbnail_resources']
        my_post['__typename'] = post['node']['__typename']

        print(json.dumps(my_post)+",", file=out_medias)
        return my_post

    def _parse_archive_periodic_media(self, my_post, out_medias_periodic):
        """
        Realiza parsing de arquivos do tipo "periodic_media"

        Parâmetros
        ----------
        my_post : Post
            objeto do tipo post do qual serão retiradas 
            as informações de interesse
        out_medias_periodic : file
            arquivo de saída em que serão compilados os
            arquivos do tipo "periodic_medias"
        
        """
        periodic_media = {}
        periodic_media["short_code"] = my_post["short_code"]
        periodic_media["likes_count"] = my_post["likes_count"]
        periodic_media["comments_count"] = my_post["comments_count"]
        periodic_media["time_epoch"] = int(time.time())
        periodic_media["time_str"] = datetime.datetime.utcfromtimestamp(periodic_media["time_epoch"])\
            .strftime('%Y-%m-%d %H:%M:%S')
        print(json.dumps(periodic_media) + ",", file=out_medias_periodic)

    def _parse_medias(self, fo_medias, fo_medias_periodic):
        """
        Itera sobre os .json de mídias de cada perfil e faz 
        a chamada para as funções de parsing de "medias" e "medias_periodic"

        Parâmetros
        ----------
        fo_medias : file
            arquivo de saída onde serão armazenadas as informações do
            tipo "media"
        fo_medias_periodic : file
            arquivo de saída onde serão armazenadas as informações do
            tipo "periodic_media"
        """
        print("{\"data\": [", file=fo_medias)
        print("{\"data\": [", file=fo_medias_periodic)
        for f in glob.glob("{}/*/*.json.xz".format(self.INPUT_DIR)):
            try:
                if "UTC" in f:
                    my_post = self._parse_archive_medias(f, fo_medias)
                    self._parse_archive_periodic_media(
                        my_post, fo_medias_periodic)

            except Exception as e:
                print(self._now_str(), "Error in file:", f, "Error:", e)
        print("{}]}", file=fo_medias)
        print("{}]}", file=fo_medias_periodic)

    def create_archives(self):
        """
        Cria pastas e arquivos de saída, faz chamadas para 
        funções que agregam comentários, posts, informações 
        de perfis
        """
        # Cria pasta onde arquivos serão armazenados
        self._create_data_folder()
        # cria os aquivos de saida esperados
        OUT_ARCHIVE_COMMENTS, OUT_ARCHIVE_MEDIAS, OUT_ARCHIVE_MEDIAS_PERIODIC, OUT_ARCHIVE_PROFILES_PERIODIC = self._create_output_paths()

        print(self._now_str(), "Creating archives at:",
              "data/archives/{}".format(self.TIME))
        # perfis e midias
        fo_medias = open(OUT_ARCHIVE_MEDIAS, "w")
        fo_medias_periodic = open(OUT_ARCHIVE_MEDIAS_PERIODIC, "w")
        fo_profiles_periodic = open(OUT_ARCHIVE_PROFILES_PERIODIC, "w")

        self._parse_medias(fo_medias, fo_medias_periodic)
        self._aggregate_profiles(fo_profiles_periodic)
        self._aggregate_comments(OUT_ARCHIVE_COMMENTS)

        fo_medias.close()
        fo_medias_periodic.close()
        fo_profiles_periodic.close()


INPUT_DIR = "data/staging"
OUTPUT_DIR = "data/archives"
INPUT_ARCHIVE_COMMENTS = "data/staging/comments.json"

ca = CreateArchives(INPUT_DIR, OUTPUT_DIR, INPUT_ARCHIVE_COMMENTS)
ca.create_archives()

#!/usr/bin/python

import sys
import os
from datetime import datetime

from data_handle import DataHandle
import local_instaloader.instaloader as localinstaloader
from data_collection import DataCollection

import json

TARGET_JSON_FOLDER = "/var/instagram-crawler/jsons/"
INPUT_JSON_FOLDER = "/var/instagram-crawler/"

# TARGET_JSON_FOLDER = "/data/jsons/"
# INPUT_JSON_FOLDER = "/data/"

DEFAULT_MAX_COMMENTS = 5000
DEFAULT_MAX_POSTS = 5000

class Coletor():
    """
    Recebe os parametros de entrada, gerencia os proxies e organiza a chamada das coletas.
    Atributos
    ----------
    data_path: str
        Pasta onde os dados da coleta serao persistidos
    instagram_user: str
        Usuario do Instagram para fazer login
    instagram_passwd: str
        Senha de usuario do Instagram para fazer login
    proxy_list: list de str
        Lista de proxies
    collection_type: str
        Se a coleta e de 'usuarios' ou 'hashtags'
    user_list : list de str
        Lista de usuarios a serem monitoradas
    hashtag_list : list de str
        Lista de palavras-chave (hashtags)
    min_date : objeto datetime
        Data limite inferior da coleta.
    max_date : objeto datetime
        Data limite superior da coleta.
    max_posts: int
        Numero maximo de posts a serem coletados no periodo
    max_comments: int
        Numero maximo de comentarios por posts a serem coletados
    Metodos
    -------
    Construtor(Json)
        Construtor da classe. Recebe uma string de json com as informacoes necessarias para a coleta.
    create_collection_pipeline()
        Inicializa o processo de coleta de acordo com os parametros de entrada.
    """
    def __init__(self, input_json):
        try:
            self.data_path = TARGET_JSON_FOLDER

            self.instagram_user = input_json['login_usuario']
            self.instagram_passwd = input_json['login_senha']

            self.proxy_list = input_json['lista_de_proxies']

            self.user_list = input_json['usuarios']
            self.hashtag_list = []

            for hashtag in input_json['palavras']:
                self.hashtag_list.append(str(hashtag).replace("#", ""))

            self.users_to_download_media = input_json['usuarios_a_baixar_midias']

            self.hashtags_to_download_media = []
            for hashtag in input_json['palavras_a_baixar_midias']:
                self.hashtags_to_download_media.append(str(hashtag).replace("#", ""))

            dataHandle = DataHandle()
            self.min_date = dataHandle.getDateFormatted(str(input_json['data_min']), only_date=True) if input_json['data_min'] is not None else None
            self.max_date = dataHandle.getDateFormatted(str(input_json['data_max']), only_date=True) if input_json['data_max'] is not None else None

            self.max_posts = input_json['maximo_posts'] if input_json['maximo_posts'] is not None else DEFAULT_MAX_POSTS
            self.max_comments = input_json['maximo_comentarios'] if input_json['maximo_comentarios'] is not None else DEFAULT_MAX_COMMENTS

            self.proxy_index = 0
            self.max_attempts = len(self.proxy_list)+1

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno, '\tData e hora: ', datetime.now(),
                  flush=True)

            print("Finalizando script...")
            sys.exit(1)


        '''
        Cria pasta de saida
        '''
        self.create_data_path()


    def create_data_path(self):
        dataHandle = DataHandle()

        self.current_timestamp = str(datetime.now().timestamp()).replace(".", "_")


        directory_list = ['{}{}/'.format(self.data_path , self.current_timestamp),
                                   '{}{}/{}/'.format(self.data_path , self.current_timestamp, "medias")]

        dataHandle.create_directories(directories_list=directory_list)

        self.data_path_source_files = '{}{}/'.format(self.data_path , self.current_timestamp)

        self.filename_posts = '{}{}/{}'.format(self.data_path , self.current_timestamp,"posts.json")
        self.filename_comments = '{}{}/{}'.format(self.data_path, self.current_timestamp, "comments.json")
        self.filename_profiles_posts = '{}{}/{}'.format(self.data_path, self.current_timestamp, "profiles_posts.json")
        self.filename_profiles_comments = '{}{}/{}'.format(self.data_path, self.current_timestamp, "profiles_comments.json")
        self.filepath_medias ='{}{}/{}/'.format(self.data_path , self.current_timestamp, "medias")

        self.filename_unified_data_file = '{}{}/{}'.format(self.data_path , self.current_timestamp,str(self.current_timestamp)+".json")

    def get_proxy(self, does_not_increment=False):
        proxies = None

        try:
            if len(self.proxy_list) > 0:
                self.proxy_index = 0 if self.proxy_index >= len(self.proxy_list) else self.proxy_index
                proxy = self.proxy_list[self.proxy_index]

                if does_not_increment is False:
                    self.proxy_index += 1

                proxies = {
                    'http': "http://"+proxy,
                    'https': "https://"+proxy
                }

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno, '\tData e hora: ', datetime.now(),
                  flush=True)

            print("Finalizando script...")
            sys.exit(1)
        finally:
            return proxies

    def getErrorDocument(self, exception_obj, exc_type, exc_tb):
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        error_str = '{}'.format(str(exception_obj))
        error_details = '{} {} {}'.format(exc_type, fname, exc_tb.tb_lineno)

        error_document = {"erro": error_str, "detalhes": error_details, "data_e_hora": str(datetime.now())}

        return error_document

    def create_error_file(self, filename_output, error_document):
        try:
            dataHandle = DataHandle()
            dataHandle.persistData(filename_output=filename_output, document_list=[error_document],
                                       operation_type="w")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno, '\tData e hora: ', datetime.now(),
                  flush=True)

            print("Finalizando script...")
            sys.exit(1)

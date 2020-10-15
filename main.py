#!/usr/bin/python

import sys
import os
from datetime import datetime

from data_handle import DataHandle
import our_instaloader.instaloader as myinstaloader
from data_collection import DataCollection

import json


TARGET_JSON_FOLDER = "/var/instagram-crawler/jsons/"
INPUT_JSON_FOLDER = "/var/instagram-crawler/"

try:
    os.makedirs(TARGET_JSON_FOLDER)
except Exception as e:
    pass

class Coletor():
    def __init__(self, input_json):
        try:
            self.data_path = TARGET_JSON_FOLDER

            self.collection_type = input_json['tipo_de_coleta']

            self.instagram_user = input_json['login_usuario']
            self.instagram_passwd = input_json['login_senha']

            self.proxy_list = input_json['lista_de_proxies']
            self.user_list = input_json['usuarios']
            self.hashtag_list = input_json['palavras']
            # self.users_to_download_media = input_json['usuarios_a_baixar_midias']

            dataHandle = DataHandle()
            self.min_date = dataHandle.getDateFormatted(str(input_json['data_minima']), only_date=True) if input_json['data_minima'] is not None else None
            self.max_date = dataHandle.getDateFormatted(str(input_json['data_maxima']), only_date=True) if input_json['data_maxima'] is not None else None

            self.max_posts = input_json['limite_de_posts']
            self.max_comments = input_json['limite_de_comentarios']
            # self.print_logs = bool(input_json['mostrar_logs_execucao'])

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
        self.__create_data_path()

    def __create_data_path(self):
        dataHandle = DataHandle()

        current_timestamp = str(datetime.now().timestamp()).replace(".", "_")


        directory_list = ['{}{}/'.format(self.data_path , current_timestamp),
                                   '{}{}/{}/'.format(self.data_path , current_timestamp, "medias")]

        dataHandle.create_directories(directories_list=directory_list)

        self.data_path_source_files = '{}{}/'.format(self.data_path , current_timestamp)

        self.filename_posts = '{}{}/{}'.format(self.data_path , current_timestamp,"posts.jsonl")
        self.filename_comments = '{}{}/{}'.format(self.data_path, current_timestamp, "comments.jsonl")
        self.filename_profiles_posts = '{}{}/{}'.format(self.data_path, current_timestamp, "profiles_posts.jsonl")
        self.filename_profiles_comments = '{}{}/{}'.format(self.data_path, current_timestamp, "profiles_comments.jsonl")
        self.filepath_medias ='{}{}/{}/'.format(self.data_path , current_timestamp, "medias")


    def __print_collection_parameters(self):
        print("users:", self.user_list)
        print("min_date:", self.min_date)
        print("max_comments:", self.max_comments)
        print("hashtags_list:", self.hashtag_list)
        print("proxy_list:", self.proxy_list)


    def __get_proxy(self):
        proxies = None

        try:
            if len(self.proxy_list) > 0:
                self.proxy_index = 0 if self.proxy_index >= len(self.proxy_list) else self.proxy_index
                proxy = self.proxy_list[self.proxy_index]

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


    def execute_data_collection(self, filename_output, dataHandle, document_input_list, debug_message, collection_type):
        collection_sucess = False
        error_document = None
        erroNotInstaloader = False

        try:
            collection_attempts = 0

            while collection_sucess is False and collection_attempts < self.max_attempts:
                prefix_str = "(Re)" if collection_attempts > 0 else " "
                a_message = "{}{}".format(prefix_str, debug_message)
                print("\n")
                print(a_message, '\tData e hora: ', datetime.now(),flush=True)

                proxy_info = self.__get_proxy()
                instaloaderInstance = myinstaloader.Instaloader(proxies=proxy_info)

                if collection_type == "posts_hashtag":
                    instaloaderInstance.login(user=self.instagram_user, passwd=self.instagram_passwd)

                dataCollection = DataCollection(filename_output=filename_output, dataHandle=dataHandle,
                                                 instaloaderInstance=instaloaderInstance,
                                                 instaloaderClass=myinstaloader,
                                                 collection_type=self.collection_type)

                if proxy_info is None:
                    print("\t!!!ATENCAO!!!: Esta coleta nao esta utilizando proxy.")
                else:
                    proxy_alias = proxy_info["https"].split("@")[1]
                    print("\tUtilizando o proxy:", proxy_alias)

                documents_collected = 0
                for document_input in document_input_list:
                    documents_collected +=1
                    if collection_type == "profiles_posts":
                        print("\tColetando perfil do usuario {}".format(document_input), '\tData e hora: ', datetime.now(),
                              flush=True)
                        has_error, error_document = dataCollection.collectProfile(username=document_input)
                    elif collection_type == "posts_profile":
                        print("\tColetando posts do usuario {} {}/{}".format(document_input["nome_do_usuario"], documents_collected, len(document_input_list)),
                              '\tData e hora: ',
                              datetime.now(), "\n",
                              flush=True)
                        has_error, error_document = dataCollection.collectPosts(data_min=self.min_date,
                                                                                 data_max=self.max_date,
                                                                                 post_limit=self.max_posts,
                                                                                 username=document_input['nome_do_usuario'],
                                                                                 hashtag=None)
                    elif collection_type == "posts_hashtag":
                        print("\tColetando posts da hashtag {}".format(document_input),
                              '\tData e hora: ', datetime.now(), "\n",
                              flush=True)
                        has_error, error_document = dataCollection.collectPosts(data_min=self.min_date,
                                                                                 data_max=self.max_date,
                                                                                 post_limit=self.max_posts,
                                                                                 username=None,
                                                                                   hashtag=document_input)
                    elif collection_type == "media":
                        print("\tColetando media do post {} {}/{}".format(document_input['identificador'], documents_collected, len(document_input_list)),'\tData e hora: ', datetime.now(), flush=True)
                        has_error, error_document = dataCollection.downloadPostMedia(
                            post_id=document_input['identificador'],
                            media_url=document_input['identificador_midia'])
                    elif collection_type == "comments":
                        print("\tColetando comments do post {} {}/{}".format(document_input['identificador'],documents_collected,len(document_input_list)),'\tData e hora: ', datetime.now(),flush=True)
                        has_error, error_document = dataCollection.collectComments(
                            post_id=document_input['identificador'],
                            comments_by_post_limit=self.max_comments,
                            line_debug_number=1000)
                    elif collection_type == "profiles_comments":
                        print("\tColetando perfil do usuario {} {}/{}".format(document_input['nome_do_usuario'], documents_collected, len(document_input_list)), '\tData e hora: ', datetime.now(),
                              flush=True)
                        has_error, error_document = dataCollection.collectProfile(username=document_input['nome_do_usuario'])
                    else:
                        print("Tipo de coleta nao identificado. Finalizando script...")
                        sys.exit(1)

                    if has_error is True:
                        if "429" in error_document:
                            print("Muitas requisicoes feitas recentemente. Erro:", error_document)
                        collection_attempts += 1
                        collection_sucess = False
                        break
                    else:
                        collection_sucess = True

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("\nProcesso de coleta sera finalizado devido a erro. O erro: ", e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno, '\tData e hora: ',datetime.now(),flush=True)
            erroNotInstaloader = True
            sys.exit(1)
        finally:
            if erroNotInstaloader is False:
                if collection_type == "medias" and collection_sucess is False:
                    print("{}{}".format("\nProcesso de coleta sera finalizado devido a erro. O erro: ",
                                        error_document), flush=True)
                    sys.exit(1)

                if collection_type != "medias" and collection_sucess is False:
                    print("{}{}".format("\nProcesso de coleta sera finalizado devido a erro. Verifique em ",
                                        filename_output), flush=True)
                    sys.exit(1)


    def create_collection_pipeline(self):
        try:
            start_time = str(datetime.now())
            dataHandle = DataHandle()

            start_time = str(dataHandle.getDateFormatted(string_datetime=start_time))

            print("Processo de coleta iniciado em {}\tSalvando dados em {}".format(start_time, self.data_path_source_files), flush=True)

            if self.collection_type != "por_usuario" and self.collection_type != "por_hashtag":
                print("\nTipo de coleta nao identificado. Finalizando script ", flush=True)
                sys.exit(1)


            if self.collection_type == "por_usuario":
                ### COLETA 1.1 - PERFIL
                document_input_list=self.user_list
                filename_output = self.filename_profiles_posts

                self.execute_data_collection(filename_output=filename_output, dataHandle=dataHandle,
                                             document_input_list=document_input_list,
                                             debug_message="Inicio da coleta de perfil de usuarios",
                                             collection_type="profiles_posts")

                ### COLETA 1.2 - POSTS DE PERFIL
                document_input_list = dataHandle.getData(filename_input=self.filename_profiles_posts, attributes_to_select=['nome_do_usuario'])
                filename_output = self.filename_posts

                if len(document_input_list) > 0:
                    self.execute_data_collection(filename_output=filename_output, dataHandle=dataHandle,
                                                                     document_input_list=document_input_list,
                                                                     debug_message="Inicio da coleta de posts de usuario",
                                                                     collection_type="posts_profile")
                else:
                    print("\nAtencao: Sem perfis armazenados para coletar posts.",flush=True)

            if self.collection_type == "por_hashtag":
                ### COLETA 1 - HASHTAGS
                document_input_list = self.hashtag_list
                filename_output = self.filename_posts

                self.execute_data_collection(filename_output=filename_output, dataHandle=dataHandle,
                                                                 document_input_list=document_input_list,
                                                                 debug_message="Inicio da coleta de posts com hashtag",
                                                                 collection_type="posts_hashtag")

            ### COLETA 2 - MIDIA DOS POSTS
            document_input_list = dataHandle.getData(filename_input=self.filename_posts,
                                                     attributes_to_select=['identificador', "identificador_midia",
                                                                           "tipo_midia"])
            filepath_output = self.filepath_medias

            if len(document_input_list) > 0:
                self.execute_data_collection(filename_output=filepath_output, dataHandle=dataHandle,
                                                                 document_input_list=document_input_list,
                                                                 debug_message="Inicio da coleta de media dos posts",
                                                                 collection_type="media")
            else:
                print("\nAtencao: Sem posts armazenados para coletar midia.", flush=True)

            ### COLETA 3 - COMENTARIOS DOS POSTS
            document_input_list = dataHandle.getData(filename_input=self.filename_posts,
                                                     attributes_to_select=['identificador'])
            filename_output = self.filename_comments

            if len(document_input_list) > 0:
                self.execute_data_collection(filename_output=filename_output, dataHandle=dataHandle,
                                             document_input_list=document_input_list,
                                             debug_message="Inicio da coleta de comments de posts",
                                             collection_type="comments")
            else:
                print("\nAtencao: Sem posts armazenados para coletar comentarios.", flush=True)

            ### COLETA 4 - PERFIL DOS COMENTADORES
            document_input_list = dataHandle.getData(filename_input=self.filename_comments,
                                                     attributes_to_select=['nome_do_usuario'])
            filename_output = self.filename_profiles_comments

            if len(document_input_list) > 0:
                self.execute_data_collection(filename_output=filename_output, dataHandle=dataHandle,
                                             document_input_list=document_input_list,
                                             debug_message="Inicio da coleta de perfil de comentadores",
                                             collection_type="profiles_comments")
            else:
                print("\nAtencao: Sem comentarios armazenados para coletar perfis de comentadores.", flush=True)


        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno, '\tData e hora: ', datetime.now(),
                  flush=True)

            print("Finalizando script...")
            sys.exit(1)



def main():
    try:
        start_time = datetime.now()

        '''
        --------------------------------------------------------
        Le dados de entrada
        '''
        try:
            cmd = sys.argv[1]
        except:
            print("Erro: Nenhuma entrada informada. Fechando script...")
            sys.exit(1)

        try:
            if cmd == "-d":
                json_dump_input = sys.argv[2]
                json_dump_input = json_dump_input.replace("'", '"')
                input_json = json.loads(json_dump_input)
            else:
                filename_data_input = sys.argv[1]
                with open(INPUT_JSON_FOLDER +filename_data_input, "r", encoding="utf-8") as file_input:
                    input_json = json.load(file_input)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('\nErro na entrada de dados: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno, '\tFechando script: ',flush=True)
            sys.exit(1)

        '''
        --------------------------------------------------------
        Testa se dados de entrada sao validos
        '''
        attributes_to_run = ['lista_de_proxies','usuarios','palavras','data_minima','data_maxima', 'limite_de_posts',
                             'limite_de_comentarios', "login_usuario","login_senha", "tipo_de_coleta"]


        attributes_not_provided = [x for x in attributes_to_run if x not in input_json]

        if len(attributes_not_provided) > 0:
            error_msg = "Erro: O atributo: {} não foi informado " if len(attributes_not_provided) == 1 else  "Erro: Os atributos: {} não foram informados "

            print(str(error_msg+"na entrada. Fechando script...").format(", ".join(attributes_not_provided)))
            sys.exit(1)

        '''

        --------------------------------------------------------
        Inicia coleta
        '''

        c = Coletor(input_json=input_json)
        c.create_collection_pipeline()

        end_time = datetime.now()
        print("\nData de inicio: %s\nData final: %s\nTempo de execucao (minutos): %s\n" % (start_time, end_time, ((end_time - start_time).seconds)/60))

        print("\n\n###########################################################\tSCRIPT FINALIZADO.", flush=True)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno, '\tData e hora: ', datetime.now(),
              flush=True)

if __name__ == '__main__':
    main()


import sys
import json
import os
import argparse
from download_medias import download_medias as dm
from followers import DownloadFollowers as df

USERS_FILENAME = "users.txt" # nao alterar
MAX_COMMENT_FILE = "max_comment_file.txt" # nao alterar

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
            print("No input mode provided. Exiting program...")
            quit()

        try: 
            if cmd == 'W':
                with open(sys.argv[2], "r") as f:
                    self.input_json = json.load(f)
            elif cmd == 'J':
                self.input_json = json.loads(" ".join(sys.argv[2:]))
            else:
                print("Input mode not available. Exiting program...")
                quit()
            print("Input mode: ", cmd)
        except:
            print("No input file provided. Exiting program...")
            quit()

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

    def _init_comandline_crawler(self, sleep_time, min_date, aux_users_filename):
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
        command = "./run_crawl.sh -p " + \
            str(aux_users_filename)+" -d " + str(min_date)
        if(sleep_time is not None):
            command = command + " -t " + str(sleep_time)

        os.system(command)

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
        self._create_users_input_file(USERS_FILENAME)
        self._create_max_comments_input_file(MAX_COMMENT_FILE)
        self._init_comandline_crawler(sleep_time, min_date, USERS_FILENAME)
        os.remove(USERS_FILENAME)
        os.remove(MAX_COMMENT_FILE)

    def _download_medias(self):
        """
        Coleta as mídias dos perfis marcados no json de entrada. Utiliza 
        um objeto de classe DownloadMedias para realizar a tarefa

        Parâmetros
        -----------
            Nenhum
        """
        print("==============================")
        print("DOWNLOADING MEDIAS")
        print("==============================")
        download_photo = dm(self.input_json)
        download_photo.download(verbose=True)

    def _download_followers(self):
        print("==============================")
        print("DOWNLOADING FOLLOWERS")
        print("==============================")
        dfollowers = df(self.input_json)
        dfollowers.download_followers()

    def init_crawler(self):
        """
        Inicializa a coleta de perfis, posts e mídias.

        Parâmetros
        -----------
            Nenhum
        """
        self._parse_json()
        self._download_medias()
        self._download_followers()

c = Coletor()
c.init_crawler()

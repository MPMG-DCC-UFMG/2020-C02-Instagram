import json
import requests
import instaloader
import os

class download_medias():
    """
    Classe para realizar o download das mídias de posts de Twitter
    ou Instagram coletados via os coletores desenvolvidos para o
    projeto do Ministério Público de Minas Gerais.

    Atributos
    ---------
    folder : str
        Nome da pasta padrão da coleta do Instagram.
    path : str
        Nome do diretório de saída para o download das mídias.
    data : list de dict
        Lista dos posts coletados. Cada post é um dict contendo
        variadas informações (texto, data, url da mídia etc).
    users : list de str
        Lista de usuários cujas mídias devem ser baixadas. Caso seja
        None, todos os usuários devem ser considerados.
    is_twitter : bool
        Verdadeiro caso seja uma coleta de Twitter, falso caso seja
        de Instagram.

    Métodos
    -------
    download(verbose)
        Função que itera pelos posts e chama as funções
        correspondente ao tipo de post (instagram ou twitter)
        para baixar as mídias (se pertencerem a um dos usuários
        pré-definidos).
    """


    def __get_folder(self):
        """
        Encontra a pasta padrão de coleta do instagram caso arquivo
        de entrada ou pasta de saída não forem fornecidos
        """
        self.folder = str(max([int(x) for x in os.listdir("data/archives")
            if x != 'staging' and x[0] != '.']))


    def __get_data(self):
        """
        Guarda em memória a lista de posts gerados pela coleta
        (seja de Instagram ou Twitter).

        Levanta
        -------
        Exception
            Caso os dados não estejam presentes ou não estejam de
            acordo com o padrão da coleta, o programa levanta uma
            exceção padrão.
        """
        try:
            out = self.__json['output']
        except:
            out = 'data/archives/' + self.folder + '/medias.json'

        with open(out, 'r') as f:
            output_json = json.load(f)

        try:
            self.is_twitter = self.__json['crawler'] == 'twitter'
            self.data = output_json['data']
        except:
            raise Exception("Arquivo não compatível.")


    def __get_path(self):
        """
        Guarda o nome do diretório destino das mídias.
        Verifica se foi especificado ou se devemos usar a pasta
        padrão do Instagram.
        """
        try: 
            self.path = self.__json['output_media']
            if self.path[-1] != '/':
                self.path += '/'
        except:
            if not os.path.exists("data/archives/"+self.folder+'/images'):
                os.makedirs("data/archives/"+self.folder+'/images')
            self.path = "data/archives/"+self.folder+'/images/'


    def __get_users(self):
        """
        Guarda quais usuários devem ser considerados na coleta.
        Verfica se estão descritos no json de entrada.
        """
        try:
            self.users = set(self.__json['users_to_download_media'])
        except:
            self.users = None


    def __init__(self, filename):
        """
        Inicia o objeto.

        Parametros
        ----------
        filename : str
            Nome do json de entrada.
        """
        with open(filename, 'r') as f:
            self.__json = json.load(f)

        self.__get_folder()
        self.__get_data()
        self.__get_path()
        self.__get_users()


    def __twitter(self, post):
        """
        Baixa as mídias de um dado post no twitter, se for de um
        usuário em users.

        Parametros
        ----------
        post : dict
            Um post de twitter que se deseja baixar as mídias (se
            existirem)
        """
        try:
            path = self.path + post['id'] + '-'
            number = 0
            if self.users is None or post['screen_name'] in self.users:
                for photo in post['medias']:
                    if photo['type'] == 'photo':
                        filename = path + str(number) + '.jpg' 
                    elif photo['type'] == 'video':
                        filename = path + str(number) + '.mp4' 
        
                    r = requests.get(photo['url']) 
                    with open(filename, 'wb') as f: 
                        f.write(r.content) 
                    number += 1
        
        except:
            return False


    def __instagram(self, post):
        """
        Baixa as mídias de um dado post no instagram, se for de um
        usuário em users.
        
        Parametros
        ----------
        post : dict
            Um post de twitter que se deseja baixar as mídias (se
            existirem)
        """
        try:
            path = self.path + post['id']
            if self.users is None or post['owner_username'] in self.users:
                if post['is_video']:
                    filename = path + '.mp4' 
                    iloader = instaloader.Instaloader()
                    get_post = instaloader.Post.from_shortcode(
                            iloader.context, post['short_code'])
                    url = get_post.video_url
                else:
                    filename = path + '.jpg' 
                    url = post['image_url']
        
                r = requests.get(url) 
                with open(filename, 'wb') as f: 
                    f.write(r.content) 
            return True
        
        except:
            return False


    def download(self, verbose=False):
        """
        Função que itera pelos posts e chama as funções
        correspondente ao tipo de post (instagram ou twitter)
        para baixar as mídias (se pertencerem a um dos usuários
        pré-definidos).

        Parametros
        ----------
        verbose : bool
            Booleano sobre se a coleta deve ser silenciosa ou
            se pequenas informações devem ser fornecidas ao
            usuário sobre o download.
        """

        if verbose:
            if self.users is None:
                print("Downloading media from all users.")
            else:
                print("Downloading media from specified users:")
                print('\t'+', '.join(self.users))

        count = 0
        for post in self.data:
            status = self.__twitter(post) if self.is_twitter \
                else self.__instagram(post)

            if not status:
                count += 1

        if count > 0 and verbose:
            print("Warning:", count, "unrecognized posts.")

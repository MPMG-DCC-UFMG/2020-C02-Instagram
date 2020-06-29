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
        self.folder = "data/archives/"
        self.folder += str(max([int(x) for x in os.listdir(self.folder)
            if x != 'staging' and x[0] != '.']))


    def __get_data(self):
        """
        Guarda em memória a lista de posts gerados pela coleta
        (seja de Instagram ou Twitter).

        Guarda o nome do diretório destino das mídias.
        Verifica se foi especificado ou se devemos usar a pasta
        padrão do Instagram.

        Levanta
        -------
        Exception
            Caso os dados não estejam presentes ou não estejam de
            acordo com o padrão da coleta, o programa levanta uma
            exceção padrão.
        """
        try:
            out = self.__json['output']
            with open(out, 'r') as f:
                self.data = json.load(f)['data']
            
            self.path = self.__json['output_media']
            if self.path[-1] != '/':
                self.path += '/'
        except:
            self.data = list()
            path = self.folder + "/staging/"
            for profile in os.listdir(path):
                output = self.folder + profile + '/medias/'
                if not os.path.exists(output):
                    os.makedirs(output)
                folder = path + profile + "/posts/"
                for post in os.listdir(folder):
                    if post[-3:] == "txt":
                        continue
                    with open(folder+post, 'r') as f:
                        data = json.load(f)['node']
                        self.data.append((data, output))

        try:
            self.is_twitter = self.__json['crawler'] == 'twitter'
        except:
            raise Exception("Arquivo não compatível.")


    def __get_users(self):
        """
        Guarda quais usuários devem ser considerados na coleta.
        Verfica se estão descritos no json de entrada.
        """
        try:
            self.users = set(self.__json['users_to_download_media'])
        except:
            self.users = None


    def __init__(self, Json):
        """
        Inicia o objeto.

        Parametros
        ----------
        filename : str
            Nome do json de entrada.
        """
        self.__json = Json
        self.__get_folder()
        self.__get_data()
        self.__get_users()

    
    def __request(self, filename, url):
        """
        Faz a requisição da mídia e escreve no disco.

        Parametros
        ----------
        filename : str
            Nome da mídia no disco.
        url : str
            Endereço url da mídia.
        """
        r = requests.get(url) 
        with open(filename, 'wb') as f: 
            f.write(r.content) 


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
        
                    self.__request(filename, photo['url'])
                    number += 1
        
        except:
            return False


    def __get_post(self, code):
        """
        Cria uma instancia do post como objeto do instaloader

        Parametros
        ----------
        code : str
            O short code do post do instagram
        """
        iloader = instaloader.Instaloader()
        return instaloader.Post.from_shortcode(iloader.context, code)


    def __instagram(self, post_tuple):
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
            post = post_tuple[0]
            path = post_tuple[1] + post['id']
            if self.users is None or post['owner']['username'] in self.users:
                if post["__typename"] == "GraphSidecar":
                    _post = self.__get_post(post["short_code"])
                    photos = _post.get_sidecar_nodes()
                    idx = 1
                    for img in photos:
                        vid = img.is_video
                        filename = path + '_' + str(idx)
                        filename += ".mp4" if vid else ".jpg"
                        url = img.video_url if vid else img.display_url
                        self.__request(filename, url)
                        idx += 1
                else:
                    if post['is_video']:
                        filename = path + '.mp4' 
                        _post = self.__get_post(post["short_code"])
                        url = _post.video_url
                    else:
                        filename = path + '.jpg' 
                        url = post['image_url']
                    
                    self.__request(filename, url)

            return True

        except Exception as e:
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

        count = -1
        for post in self.data:
            status = self.__twitter(post) if self.is_twitter \
                else self.__instagram(post)

            if not status:
                count += 1

        if count > 0 and verbose:
            print("Warning:", count, "missing posts.")

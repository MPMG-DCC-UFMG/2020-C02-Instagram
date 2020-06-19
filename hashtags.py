from instaloader import Instaloader
from instaloader import Hashtag
import os
import datetime


class DownloadHashtags():
   """
    Classe para inicializar o coletor. Realiza a leitura da entrada via
    argumento de linha de comando, e passa para os módulos que coletam 
    as informações de cada perfil, assim como o download das mídias dos
    perfis selecionados. 

    Atributos
    -----------
    input_json : dict
         Dicionário com as informações da entrada
    hashtags_list : list
         Lista de de hashtags que devem ser coletadas
    hashtags_max : int
         Número máximo de posts por hashtag que devem ser coletados
    time : int
         Timestamp do horário da coleta. Importante para gerar as 
         saídas nas pastas corretas
        

    Métodos
    -----------
    download_hashtags()
        Método que realiza o download de hashtags especificadas na entrada

    """
   def __init__(self, Json):
      """
      Inicializa o objeto

      Parâmetros
      ------------
         Json : dict
            Dicionário com as informações da entrada
      """
      self.input_json_data = Json
      self.hashtags_list = self.input_json_data["hashtags_list"]
      self.hashtags_max = self.input_json_data["hashtags_max"]
      self.time = int(datetime.datetime.now().replace(
            microsecond=0).timestamp())

   def _get_path(self):
      """
      Retorna o nome do diretório destino das mídias.
      Verifica se foi especificado ou se devemos usar a pasta
      padrão do Instagram.
      """
      
      folder = str(self.time)

      if not os.path.exists("data/archives/"+folder+'/hashtags'):
         os.makedirs("data/archives/"+folder+'/hashtags')
      path = "data/archives/"+folder+'/hashtags/'
      return path


   def download_hashtags(self):
      """
      Método que realiza o download de hashtags especificadas na entrada
      """
      L = Instaloader()
      for hs in self.hashtags_list:
         hashtag = Hashtag.from_name(L.context, hs)
         post_counter = 0
         for post in hashtag.get_posts():
            L.download_post(post, target=hashtag.name)
            post_counter = post_counter + 1
            if self.hashtags_max != None:
               if post_counter == self.hashtags_max:
                  break
               
         print("Downloaded ", post_counter," from ",hashtag.name)
         os.rename(hashtag.name,self._get_path()+hashtag.name)
      
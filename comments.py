#!/usr/bin/env python3

import json
import time
import lzma
import glob
from datetime import datetime
import timeout_decorator
import instaloader
import sys
import os


TIMEOUT = 7200


@timeout_decorator.timeout(TIMEOUT)
class DownloadComments():
    """
    Classe para coletar comentários de posts do instagram. Utiliza os posts
    coletados pela interface de linha de comando do Instaloader para isso

    Atributos
    ---------
    max_comments : int
        máximo de comentários *por post* que devem ser coletados

    input_dir : str
        nome da pasta em que se encontram os dados dos perfis coletados

    Métodos
    ---------
    download_comments()
        Função que itera sobre as pastas dos perfis coletados, obtêm os códigos 
        de posts de cada uma e dispara a coleta dos comentários para cada post

    """
    def __init__(self, max_comments, input_dir):
        """
        Inicializa o objeto

        Parâmetros
        ---------
        max_comments : int
            máximo de comentários *por post* que devem ser coletados

        input_dir : str
            nome da pasta em que se encontram os dados dos perfis coletados
        """
        self.max_comments = max_comments
        self.input_dir = input_dir

    def _collect_comments(self, media_codes_list, outfile, iloader):
        """
        Itera sobre a lista de códigos de post coletados. Dispara a coleta
        dos comentários de cada post. É feito parsing em cima dos comentários
        e respostas a comentaŕios de cada post.

        Parâmetros
        ---------
        medias_codes_list : list(str)
            lista dos códigos de mídia dos posts

        outfile : str
            nome do arquivo de saída onde serão armazenados os comentários

        iloader : Instaloader()
            instância do instaloader utilizada para coleta de comentários
        """
        post_counter = 1
        for code in media_codes_list:
            print(self._now_str(), "Crawling post ", post_counter,
                  "of ", len(media_codes_list), " --- ", code)
            post_counter = post_counter + 1
            try:
                n_comm = 0
                # usa o instaloader instanciado e um codigo de midia para coletar os comentarios daquele post
                comments = self._get_comments_safe(iloader, code)

                for comment in comments:
                    self._parse_comment(comment, outfile, code)
                    for reply in comment.answers:
                        self._parse_comment_replies(
                            comment, reply, outfile, code)
                    n_comm += 1

                print(self._now_str(), "Crawled", n_comm, "comments")

            except timeout_decorator.TimeoutError as e:  # lida com excecoes de tempo esperando p/ coleta e erro
                print(self._now_str(), "Timeout for post", code)
            except Exception as e:
                print(self._now_str(), "Error for post", code)

    def _parse_comment_replies(self, parent_comment, reply, outfile, media_code):
        """
        Método que realiza parsing de comentários que são respostas a outros 
        comentários, retirando apenas as informações relevantes e 
        armazenando em um json que será armazenado em um arquivo externo

        Parâmetros
        ---------
        parent_comment : Comment
            objeto do tipo comentário ao qual o comentário atual está respondendo
        reply : Comment
            Comentário atual, resposta ao parent_comment
        outfile : str
            nome do arquivo onde serão os json gerados para cada comentário
        media_code : str
            código do post de onde o comentário foi coletado
        """
        my_reply = {}
        my_reply["text"] = reply.text
        my_reply["created_time"] = int(reply.created_at_utc.timestamp())
        my_reply["created_time_str"] = reply.created_at_utc.strftime(
            '%Y-%m-%d %H:%M:%S')
        my_reply["media_code"] = media_code
        my_reply["id"] = str(reply.id)
        my_reply["owner_username"] = reply.owner.username
        my_reply["owner_id"] = str(reply.owner.userid)
        my_reply["parent_comment_id"] = str(parent_comment.id)

        text = my_reply['text']
        tags = {tag.strip("#").strip(',<.>/?;:\'"[{]}\\|=+`~!@#$%^&*()').lower()
                for tag in text.split() if tag.startswith("#")}
        users = {tag.strip("@").strip(',<.>/?;:\'"[{]}\\|=+`~!@#$%^&*()').lower()
                 for tag in text.split() if tag.startswith("@")}
        my_reply['tags'] = list(tags)
        my_reply['mentioned_usernames'] = list(users)

        print(json.dumps(my_reply), file=outfile)

    def _parse_comment(self, comment, outfile, media_code):
        """
        Realiza parsing em cada objeto do tipo "Comment" retornado pelo instaloader,
        retirando apenas as informações relevantes e armazenando em um json que será
        armazenado em um arquivo externo

        Parâmetros
        ---------
        comment : Comment
            objeto do tipo comentário retornado pelo instaloader
        outfile : str
            nome do arquivo onde serão os json gerados para cada comentário
        media_code : str
            código do post de onde o comentário foi coletado
        """
        my_comment = {}
        my_comment["text"] = comment.text
        my_comment["created_time"] = int(comment.created_at_utc.timestamp())
        my_comment["created_time_str"] = comment.created_at_utc.strftime(
            '%Y-%m-%d %H:%M:%S')
        my_comment["media_code"] = media_code
        my_comment["id"] = str(comment.id)
        my_comment["owner_username"] = comment.owner.username
        my_comment["owner_id"] = str(comment.owner.userid)
        my_comment["parent_comment_id"] = None

        text = my_comment['text']
        tags = {tag.strip("#").strip(',<.>/?;:\'"[{]}\\|=+`~!@#$%^&*()').lower()
                for tag in text.split() if tag.startswith("#")}
        users = {tag.strip("@").strip(',<.>/?;:\'"[{]}\\|=+`~!@#$%^&*()').lower()
                 for tag in text.split() if tag.startswith("@")}
        my_comment['tags'] = list(tags)
        my_comment['mentioned_usernames'] = list(users)

        print(json.dumps(my_comment), file=outfile)

    def _now_str(self):
        """
        Retorna um timestamp do momento em que a função é chamada
        """
        return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

    # retorna os comentarios dado um identificador de post (shortcode)
    def _get_comments_safe(self, il, short_code):
        """
        Retorna os comentários coletados de um post

        Parâmetros
        ----------
        il : Instaloader
            instância do instaloader criada para coletar os comentários
        short_code : str
            Código do post cujos comentários serão coletados
        """
        post = instaloader.Post.from_shortcode(il.context, short_code)
        n_comm = 0
        comments = []
        for c in post.get_comments():
            comments.append(c)
            n_comm += 1
            if n_comm >= self.max_comments:
                print(self._now_str(), "Comment limit ({}) reached".format(
                    self.max_comments))
                break
        return comments

    def _collect_media_codes(self, current_profile):
        """
        Coleta os códigos do post feito por um perfil

        Parâmetros
        ----------
        current_profile : str
            nome do perfil de onde serão retirados os códigos de post
        """
        codes = set()
        # essa parte coleta os codigos identificadores do post/midia
        for f in os.listdir(self.input_dir+"/"+current_profile):
            # if f.endswith("UTC.json.xz"):
            if "UTC.json" in f:
                try:
                    media = json.loads(lzma.open(
                        self.input_dir+"/"+current_profile+'/'+str(f), "r").read().decode("utf-8"))
                    media_code = media["node"]["shortcode"]
                    codes.add(media_code)
                except:
                    print(f)
                    print("Marformed json line")

        return codes

    def download_comments(self):
        """
        Dispara o download de comentários feitos em posts coletados. Itera
        sobre as pastas de perfis coletados, disparando coleta, parsing e 
        armazenamento dos comentários.
        """
        # as pastas tem como nome o username de cada usuario
        folders = sorted(os.listdir(self.input_dir))
        n_folders = len(folders)
        for count in range(n_folders):
            current_profile = folders[count]
            print("Collecting profile", (count+1), "of",
                  n_folders, "---", current_profile)
            OUTFILE = self.input_dir+"/"+current_profile+"/comments_"+current_profile+".json"

            codes = self._collect_media_codes(current_profile)

            fo = open(OUTFILE, "a+")
            iloader = instaloader.Instaloader()
            media_codes_list = sorted(codes)

            self._collect_comments(media_codes_list, fo, iloader)

            fo.close()
            print("\n--- Finished Crawling comments from ",
                  current_profile, "---\n")

        print(self._now_str(), "Finished")

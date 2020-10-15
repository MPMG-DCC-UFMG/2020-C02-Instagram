#!/usr/bin/python

import sys
import os
from datetime import datetime

class DataCollection:
    def __init__(self, filename_output, dataHandle, instaloaderInstance, instaloaderClass,
                 collection_type):
        self.filename_output = filename_output
        self.dataHandle = dataHandle
        self.instaloaderInstance = instaloaderInstance
        self.instaloaderClass = instaloaderClass
        self.collection_type = collection_type

    def set_instaloaderInstance(self, instaloaderInstance):
        self.instaloaderInstance = instaloaderInstance

    def set_instaloaderClass(self, instaloaderClass):
        self.instaloaderClass = instaloaderClass

    def __getErrorDocument(self, exception_obj, exc_type, exc_tb):
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        error_str = '{}'.format(str(exception_obj))
        error_details = '{} {} {}'.format(exc_type, fname, exc_tb.tb_lineno)

        error_document = {"erro": error_str, "detalhes": error_details, "data_e_hora": str(datetime.now())}

        return error_document

    def __getProfileDocument(self, profile_object):
        user_profile = {"identificador": str(profile_object.userid),
                        "nome_do_usuario": profile_object.username,
                        "nome_completo": profile_object.full_name,
                        "localizacao": None,
                        "numero_de_seguidores": profile_object.followers,
                        "numero_de_seguidos": profile_object.followees,
                        "biografia": profile_object.biography,
                        "tipo_de_coleta": self.collection_type}

        return user_profile

    def collectProfile(self, username):
        user_profile_document = None
        has_error = False
        try:
            profile = self.instaloaderClass.Profile.from_username(self.instaloaderInstance.context, username)

            user_profile_document = self.__getProfileDocument(profile_object=profile)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            user_profile_document = self.__getErrorDocument(exception_obj=e, exc_type=exc_type, exc_tb=exc_tb)
            has_error = True

        finally:
            operation_type = "w" if has_error == True else "a"

            self.dataHandle.persistData(filename_output=self.filename_output,
                                        document_list=[user_profile_document],
                                        operation_type=operation_type)

            error_document = user_profile_document if has_error is True else None

            return(has_error,error_document)


    def collectPosts(self, data_min, data_max, post_limit, username=None,hashtag=None):
        inserted_posts = 0
        error_document = None
        has_error = False

        try:
            if username is not None:
                instragram_source_object = self.instaloaderClass.Profile.from_username(self.instaloaderInstance.context, username)

            else:
                instragram_source_object = self.instaloaderClass.Hashtag.from_name(self.instaloaderInstance.context, name=hashtag)

            posts = instragram_source_object.get_posts()

            for post in posts:
                try:
                    post_date = self.dataHandle.getDateFormatted(str(post.date))
                    if post_limit is not None and inserted_posts >= post_limit:
                        break

                    if hashtag is None and data_min is not None and  post_date < data_min:
                        break

                    if hashtag is None and data_max is not None and post_date > data_max:
                        pass
                    else:
                        ### Testa no caso de hashtag pois nao ha garantia de ordenamento
                        if hashtag is None or (hashtag is not None and post_date >= data_min and post_date <= data_max):
                            inserted_posts +=1
                            print("\tPosts coletados: {}\tData postagem {} ".format(inserted_posts, str(post.date)),
                                  '\tData e hora: ', datetime.now(), flush=True)

                            post_document = self.__getPostDocument(post_object=post)

                            self.dataHandle.persistData(filename_output=self.filename_output,
                                                        document_list=[post_document],
                                                        operation_type="a")

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    error_document = self.__getErrorDocument(exception_obj=e, exc_type=exc_type, exc_tb=exc_tb)
                    has_error = True
                    break

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_document = self.__getErrorDocument(exception_obj=e, exc_type=exc_type, exc_tb=exc_tb)
            has_error = True
        finally:
            if has_error is True:
                self.dataHandle.persistData(filename_output=self.filename_output,
                                            document_list=[error_document],
                                            operation_type="w")

            return (has_error, error_document)
        
    def __getPostDocument(self, post_object):

        post_document = {"identificador": post_object.shortcode,
                        "identificador_usuario":post_object.owner_id,
                        "texto": post_object.caption,
                        "numero_likes": int(post_object.likes),
                        "numero_comentarios": int(post_object.comments),
                        "data_postagem": str(self.dataHandle.getDateFormatted(str(post_object.date))),
                        "localizacao": post_object.location,
                        "tipo_midia": "imagem" if post_object.typename == "GraphImage" else ("video" if post_object.typename == "GraphVideo" else "imagem"),
                        "identificador_midia": post_object.video_url if post_object.typename == "GraphVideo" else post_object.url,
                        "tipo_de_coleta": self.collection_type
                        }

        return(post_document)


    def downloadPostMedia(self, post_id, media_url):
        has_error = False
        error_document = None
        try:
            media_filename = str(self.filename_output+str(post_id))

            if (os.path.exists(media_filename) is False):
                self.instaloaderInstance.download_pic(filename=media_filename, url=media_url, mtime=datetime.now())


        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            has_error = True
            error_document = self.__getErrorDocument(exception_obj=e, exc_type=exc_type, exc_tb=exc_tb)

        finally:
            return (has_error, error_document)



    def __getCommentDocument(self, post_id, comment_obj):
        comment_document = None
        try:
            comment_document = {"identificador": str(comment_obj.id),
                                "identificador_post": str(post_id),
                                "identificador_usuario": str(comment_obj.owner.userid),
                                "nome_do_usuario": str(comment_obj.owner.username),
                                "data_comentario": str(comment_obj.created_at_utc),
                                "texto": comment_obj.text,
                                "numero_likes": comment_obj.likes_count
                                }
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('\nErro: ', e, '\tDetalhes: ', exc_type, fname, exc_tb.tb_lineno, '\tData e hora: ', datetime.now(),
                  flush=True)
        finally:
            return(comment_document)


    def collectComments(self, post_id, comments_by_post_limit, line_debug_number = 1000):
        error_document = None
        has_error = False

        try:
            post = self.instaloaderClass.Post.from_shortcode(self.instaloaderInstance.context, post_id)

            comments = post.get_comments()

            inserted_comments = 0

            for comment in comments:
                inserted_comments += 1
                if inserted_comments % line_debug_number == 0:
                    print("\t\tColetando comentario numero {}".format(inserted_comments), '\tDatetime: ',
                          datetime.now(), flush=True)

                document = self.__getCommentDocument(post_id=post_id, comment_obj=comment)

                self.dataHandle.persistData(filename_output=self.filename_output,
                                            document_list=[document],
                                            operation_type="a")

                if (comments_by_post_limit is not None and inserted_comments > comments_by_post_limit):
                    # print("\tFinalizando coleta de comentarios do post {}. Limite de comentarios atingido.")
                    break

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            error_document = self.__getErrorDocument(exception_obj=e, exc_type=exc_type, exc_tb=exc_tb)
            has_error = True

        finally:
            operation_type = "w" if has_error == True else "a"

            self.dataHandle.persistData(filename_output=self.filename_output,
                                        document_list=[error_document],
                                        operation_type=operation_type)

            return (has_error, error_document)
from sys import argv
import json
import requests
import instaloader
import os


def twitter(post, users, path):
    """
    Baixa as mídias de um dado post no twitter, se for de um
    usuário em users.

    Parametros
    ----------
    post : dict
        Um post de twitter que se deseja baixar as mídias (se existirem)
    users : set
        Set de screen names de usuários cujas mídias devem se baixadas
        Se users for None, todos os usuários serão considerados.
    path : str
        O diretório no qual se deseja salvar as mídias.
    """
    try:
        path += '/' + post['id'] + '-'
        number = 0
        if users is None or post['screen_name'] in users:
            for photo in post['medias']:
                if photo['type'] == 'photo':
                    filename = path + str(number) + '.jpg'
                elif photo['type'] == 'video':
                    filename = path + str(number) + '.mp4'
                else:
                    # TODO
                    continue

                r = requests.get(photo['url'])
                with open(filename, 'wb') as f:
                    f.write(r.content)

                number += 1

    except:
        return False


def instagram(post, users, path):
    """
    Baixa as mídias de um dado post no instagram, se for de um
    usuário em users.

    Parametros
    ----------
    post : dict
        Um post de twitter que se deseja baixar as mídias (se existirem)
    users : set
        Set de screen names de usuários cujas mídias devem se baixadas
        Se users for None, todos os usuários serão considerados.
    path : str
        O diretório no qual se deseja salvar as mídias.
    """
    try:
        path += post['id']
        if users is None or post['owner_username'] in users:
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


# Leitura do json de entrada
if len(argv) != 2:
    raise Exception(
        "Número incorreto de parâmetros.\nUse: python3 download.py <input-json>")

with open(argv[1], 'r') as f:
    input_json = json.load(f)

# Leitura do json de saída
try:
    out = input_json['output']
except:
    folder = str(max([int(x) for x in os.listdir("data/archives")
                      if x != 'staging' and x[0] != '.']))
    out = 'data/archives/' + folder + '/medias.json'

with open(out, 'r') as f:
    output_json = json.load(f)

# Leitura da pasta onde salvar as imagens
try:
    path = input_json['output_media']
    if path[-1] != '/':
        path += '/'
except:
    folder = str(max([int(x) for x in os.listdir("data/archives")
                      if x != 'staging' and x[0] != '.']))
    if not os.path.exists("data/archives/"+folder+'/images'):
        os.makedirs("data/archives/"+folder+'/images')
    path = "data/archives/"+folder+'/images/'

# Leitura adicional
try:
    is_twitter = input_json['crawler'] == 'twitter'
    data = output_json['data']
except:
    raise Exception("Arquivo não compatível.")

try:
    users = set(input_json['users_to_download_media'])
    print("Downloading media from specified users:")
    print('\t'+', '.join(users))
except:
    users = None
    print("Downloading media from all users.")


# Download das mídias
count = 0
for post in data:
    status = twitter(post, users, path) if is_twitter \
        else instagram(post, users, path)

    if not status:
        count += 1

if count > 0:
    print("Warning:", count, "unrecognized posts.")

# Coletor para o Instagram

Coleta perfis com utilizando [instaloader](https://instaloader.github.io/) e armazena localmente

### Uso
Faz download de mídias e comentários de uma lista de perfis, dada uma data de início para a coleta

Execute com:
```
./run_crawl.sh -p profile_file [-d min_date] [-s archive_store_days] [-t sleep_time] [-n]
```
Os argumentos são:
* `profile_file`: Arquivo contendo os nomes de usuário dos perfis alvo da coleta, um por linha, como no exemplo.
* `min_date`: Data de início da coleta. O default é ontem, caso uma data não seja específicada. O formato da data deve ser `YYYY,MM,DD`, sem zeros à esquerda. Exemplo: 20/03/2020, deve-se *remover* os zeros à esquerda, da seguinte forma: 2020,3,20
* `archive_store_days`: Quantidade de dias para armazenar arquivos não copiados. Default é `2`.
* `sleep_time`: Tempo (em segundos) de espera entre coleta de perfis. Default é `0`.
* `-n`: Não deletar arquivos em staging e arquivos antigos.

 É possível utilizar `crontab` para facilitar a utilização:
```
0 23 * * * ~/instagram_crawler_batch/run_crawl.sh -p all_it.txt -t 20 > /tmp/instagram_crawler_batch_log_$( date +\%Y_\%m_\%d_\%H_\%M_\%S ) 2>&1
```

### Pacotes
Python3 com os seguintes pacotes nas versões especificadas

Name: instaloader
Version: 4.2.9
Name: timeout-decorator
Version: 0.4.1

Se utilizar o anaconda, pode ser que haja algum problema com a instalação do timeout-decorator. Melhor usar o PIP

### Obs
* Lembrar também de dar permisão aos arquivos: chmod +x script

## Scripts

### run_crawl.sh
Realiza o parsing inicial dos argumentos da linha de comando e executa os demais scripts. Tem alguns argumentos default salvos, mas o ideal é especificar sempre que usar.


### 1_download.sh

Recebe os argumentos obtidos no script run_crawl.sh: arquivo com os usernames, data inicial para coleta, tempo de espera entre coleta de perfis, caminho para a pasta onde serão salvos os arquivos, além de username e password que são argumentos opcionais.

Este script lê um usuário por vez e passa como entrada para o instaloader, junto com os demais parâmetros especificados. O instaloader gera um log que é salvo na pasta /tmp/. Esse log é apresentado no terminal ao executar o código.


### 1_download_comments.py

Utiliza os arquivos .xz para coletar os códigos identificadores de mídias/posts. Em seguida, utliza a interface do instaloader para coletar todos os comentários daquele post. Caso um comentário tenha respostas, coleta essa informação
deixando explícito qual o comentário pai e qual o filho.

### 2_create_archives.py
Utiliza os arquivos de comentário e posts gerados para cada usuário. Apenas concatena
os comentários e informações sobre os posts obtidos pelo instaloader em dois arquivos
únicos para cada coleta (comments.json e medias.json).

### 3_download_medias.py
Executa após a coleta. Itera pelos post, faz a requisição de cada uma das mídias (fotos ou vídeos) e salva dentro da pasta *images* do *archives* correspondente.

### download_medias.py
Aqui define-se a classe que de fato realiza as requisições das mídias do script anterior.

## Arquivos

### Pastas
O código cria uma pasta chamada "data", com duas subpastas:

* Pasta staging: separa os perfis em pastas, com um json específico para para os comentários daquele perfil, assim como um json para cada post coletado (o nome do arquivo corresponde ao timestamp de postagem)
* Pasta archives: separa por coletas (o nome da pasta é o timestamp do horário da coleta), contêm arquivos sobre os comentários (comments.json) e mídias (medias.json) de toda a coleta.

Dentro da pasta `data/staging/` temos as pastas salvas para cada usuário coletado.
Dentro da pasta de um usuário (ex: `data/staging/minsaude`), são armazenadas algumas informações: para cada usuário, baixa-se a foto de perfil, comentários para os posts do período especificado, id dada ao usuário, arquivo com informações sobre o usuário coletado e sobre as mídias dos posts coletados.


__Arquivo Id__: Contêm a id dada aquele perfil na coleta.

__Arquivos de Mídias__: Cada arquivo tem como título a timestamp de postagem do post coletado. Compreende informações sobre as mídias, bio do dono do post e algumas informações adicionais.

__Arquivo de Comentários__: Tem formato `comments_$USERNAME.json` e contêm todos os comentários dos posts coletados. Cada comentário tem os campos:
* text: texto do comentário
* created_time: timestamp da criação do comentário
* created_time_str: horário da criação em formato string
* media_code: identificador que o instagram usa em suas urls ex: www.instagram.com/p/B-F_9kMneA4/
* id: id gerado para o comentário
* owner_username: username do usuário que fez o comentário
* owner_id: id gerada para o dono do comentário
* tags: tags que o usuário usou no comentário
* mentioned_usernames: usernames que o dono do comentário citou
* parent_comment_id: se o comentário é uma resposta a outro, identifica qual o comentário original utilizando sua ID

__Arquivo de Informações do Perfil__: Tem formato `$USERNAME_$ID.json` e tem informações gerais sobre o perfil coletado.

# Instagram Crawler Batch
Crawl profiles with instaloader, and create archives containing the data.

## Usage
Download from a list of profiles all medias and comments for the previous day(s).

Run it with:
```
./run_crawl.sh -p profile_file [-d min_date] [-s archive_store_days] [-t sleep_time] [-n]
```
Arguments are:
* `profile_file`: a file containing the target profile usernames, one per line. Lines starting by `#` are comments.
* `min_date`: Minimum date for posts to be downloaded. Default is yesterday. Format must be `YYYY,MM,DD` without leading zeros.
* `archive_store_days`: Days to store non copied archives. Default `2`.
* `sleep_time`: Sleep seconds between crawling consectuvie profiles. Default `0`.
* `-n`: Do not delete staging files and old archives.

 Put it into a `crontab` for easy use. Like:
```
0 23 * * * ~/instagram_crawler_batch/run_crawl.sh -p all_it.txt -t 20 > /tmp/instagram_crawler_batch_log_$( date +\%Y_\%m_\%d_\%H_\%M_\%S ) 2>&1
```

## Dependencies
You need Python3 with `instaloader`.

##Obs
* Ao especificar a data, por exemplo: 20/03/2020, deve-se *remover* os zeros à esquerda, deixando no formato YYYY,MM,DD da seguinte forma: 2020,3,20
* Lembrar também de dar permisão aos arquivos: chmod +x script

## Arquivo users.txt
Neste arquivo, é só seguir o exemplo que deixei: um username por linha

## Pacotes
Alguns pacotes que precisam estar nessas versões específicas (testei em duas máquinas e aparentemente estes são realmente cruciais que estejam nessas versões específicas). O timeout-decorator não consegui instalar via anaconda, apenas por PIP.

Name: instaloader
Version: 4.2.9
Name: timeout-decorator
Version: 0.4.1

## Pastas
O código cria uma pasta chamada "data", com duas subpastas:

* Pasta staging: separa os perfis em pastas, com um json específico para para os comentários daquela pessoa
* Pasta archives: separa por coletas (o nome da pasta é um timestamp), contêm arquivos sobre os comentários (comments.json) e mídias (medias.json)

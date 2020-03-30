# Coletor para o Instagram

Coleta perfis com utilizando [instaloader](https://instaloader.github.io/) e armazena localmente

## Uso
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

## Pacotes
Python3 com os seguintes pacotes nas versões especificadas

Name: instaloader
Version: 4.2.9
Name: timeout-decorator
Version: 0.4.1

Se utilizar o anaconda, pode ser que haja algum problema com a instalação do timeout-decorator. Melhor usar o PIP

## Pastas e arquivos
O código cria uma pasta chamada "data", com duas subpastas:

* Pasta staging: separa os perfis em pastas, com um json específico para para os comentários daquela pessoa
* Pasta archives: separa por coletas (o nome da pasta é um timestamp), contêm arquivos sobre os comentários (comments.json) e mídias (medias.json)

##Obs
* Lembrar também de dar permisão aos arquivos: chmod +x script

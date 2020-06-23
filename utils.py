import lzma
import os

def extract_files(dirname):
    """
    Extrai os arquivos .json.xz obtidos pela coleta localmente
    e remove os originais. Faz a busca em profundidade em todo
    o conteúdo do diretório fornecido.

    Parametros
    ----------
    dirname : str
        Nome do diretório raiz da busca
    """
    for filename in os.listdir(dirname):
        name = dirname + "/" + filename
        if os.path.isfile(name) and name[-8:] == ".json.xz":
            with lzma.open(name, mode='rt', encoding='utf-8') as f1:
                with open(name[:-3], 'w') as f2:
                    for line in f1:
                        f2.write(line + "\n")
            os.remove(name)

        elif os.path.isdir(name):
            extract_files(name)

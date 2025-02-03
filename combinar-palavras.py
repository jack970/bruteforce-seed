import itertools
import multiprocessing
import os
import time
from mnemonic import Mnemonic
from bip32utils import BIP32Key

# Caminho do arquivo com as 44 palavras
arquivo_lista_palavras = "palavras-encontradas.txt"

# Chave pública esperada (substituir pela sua chave pública real para comparação)
carteira_esperada = "1EciYvS7FFjSYfrWxsWYjGB8K9BobBfCXw"

# salvar progresso
arquivo_progresso = "progresso.txt"
ultima_chame_arquivo = "ultima_chave.txt"

# Ler lista de palavras
with open(arquivo_lista_palavras, "r", encoding="utf-8") as f:
    palavras = f.read().splitlines()

# Função para verificar se a frase é válida
def verificar_chave(frase):
    try:
        mnemo = Mnemonic("portuguese")
        seed = mnemo.to_seed(frase)

        bip32_key = BIP32Key.fromEntropy(seed)
        chave_privada = bip32_key.WalletImportFormat()
        carteira_gerada = bip32_key.Address()

        salvar_ultima_chave(chave_privada, carteira_gerada, frase)
        return carteira_gerada == carteira_esperada
    except Exception as e:
        return False

# Função para testar combinações
def testar_combinacoes(combinacao):
    frase_teste = " ".join(combinacao)

    if verificar_chave(frase_teste):
        print("Frase encontrada:", frase_teste)
        return frase_teste
    return None


def carregar_progresso():
    if os.path.exists(arquivo_progresso):
        with open(arquivo_progresso, "r") as f:
            return int(f.read().strip())
    return 0

# Função para salvar o progresso
def salvar_progresso(indice):
    with open(arquivo_progresso, "w") as f:
        f.write(str(indice))

def salvar_ultima_chave(chave, endereco, frase):
    with open(ultima_chame_arquivo, "w") as f:
        f.write(f'{endereco} | {chave} | {frase}')

# Função para processar um chunk de combinações
def processar_chunk(args):
    chunk, inicio = args
    count = 0
    start_time = time.time()
    for i, combinacao in enumerate(chunk, start=inicio + 1):
        # print(i, combinacao)
        resultado = testar_combinacoes(combinacao)
        if resultado:
            return resultado
        salvar_progresso(i)
        count += 1
    elapsed_time = time.time() - start_time
    if elapsed_time > 0:
         print(f"Worker processou {count} combinações a uma taxa de {count / elapsed_time:.2f}/s.")
    return None


if __name__ == "__main__":
    # Gerar todas as combinações de 12 palavras sem repetição
    combinacoes = itertools.combinations(palavras, 12)

    # Carregar o último índice salvo
    ultimo_indice = carregar_progresso()
    combinacoes_restantes = itertools.islice(combinacoes, ultimo_indice, None)
    
    # Número de combinações a processar por execução
    comb_por_execucao = 100000

    # Criar os chunks para multiprocessamento
    # num_processos = min(multiprocessing.cpu_count(), comb_por_execucao)
    num_processos = 5
    chunk_size = comb_por_execucao // num_processos
    
    # Criar os chunks para multiprocessamento
    chunks = [list(itertools.islice(combinacoes_restantes, chunk_size)) for _ in range(num_processos)]
    args_list = [(chunk, ultimo_indice + i * chunk_size) for i, chunk in enumerate(chunks)]

    with multiprocessing.Pool(processes=num_processos) as pool:
        resultados = pool.map(processar_chunk, args_list)
        resultados = [res for res in resultados if res is not None]

    if resultados:
        print("Frase correta encontrada:", resultados[0])
    else:
        print("Nenhuma frase válida encontrada.")

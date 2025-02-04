import itertools
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins

class BruteForceSeed:
    def __init__(self) -> None:
        # self.carteira_esperada = "1EciYvS7FFjSYfrWxsWYjGB8K9BobBfCXw"
        self.carteira_esperada = "1CrmJ6RqsXrdHP7QYskX18cJSVJ8z6kE58"
        
    def process_combination_sequence(self, combo, insert_progress, threads_progress, futures):
        try:
            seed = Bip39SeedGenerator(combo).Generate()
            bip44 = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).DeriveDefaultPath()
            address = bip44.PublicKey().ToAddress()
            
             # Obter a chave privada e endereço da carteira
            if address == self.carteira_esperada:
                print("Encontrado", combo)
                return combo

        except Exception as e:
            pass

    def generate_combinations(self, words, num_words, num_threads, type_gen):
        mnemo = Mnemonic("portuguese")
        
        total_combinations = itertools.combinations(words, num_words)
        insert_progress = tqdm(desc="Gerando seeds", unit=" seeds", position=2)
        # Inicializa a barra de progresso das threads ativas
        threads_progress = tqdm(desc="Threads em execução", position=0)

        try:
            combinations_progress = tqdm(desc="Gerando combinações aleatórias", unit=" frases", position=1)
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = set()

                try:
                    for combo in total_combinations:
                        combo_str = ' '.join(combo)
                        combinations_progress.update(1)
                        
                        future = executor.submit(self.process_combination_sequence, combo_str, insert_progress, threads_progress, futures)

                        # Atualiza a barra de progresso das threads ativas
                        threads_progress.n = len(futures)
                        threads_progress.refresh()

                except KeyboardInterrupt:
                    print("\nInterrompendo Threads...")
                
                finally:
                    combinations_progress.close()
                    threads_progress.close()

            for future in as_completed(futures):
                future.result()  # Garante que todas as threads sejam concluídas
                # hardware_progress.close()

                # Atualiza o progresso das threads ativas
                threads_progress.n = len(futures)
                threads_progress.refresh()


        except Exception as e:
            print(f"Erro em gerar combinações: {e}")

        finally: 
            combinations_progress.close()
            threads_progress.close()
            

if __name__ == "__main__":
    arquivo_lista_palavras = "palavras-encontradas.txt"
    with open(arquivo_lista_palavras, "r", encoding="utf-8") as f:
        palavras = f.read().splitlines()

    bf = BruteForceSeed()
    bf.generate_combinations(palavras, 12, 4, None)
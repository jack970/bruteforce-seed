import itertools
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins
from mongodb_manager import MongoDBManager
from mnemonic import Mnemonic


def load_words_file(words_file):
    with open(words_file, "r", encoding="utf-8") as f:
            return f.read().splitlines()
    


class BruteForceSeed:
    def __init__(self, carteira_esperada="1EciYvS7FFjSYfrWxsWYjGB8K9BobBfCXw",  progress_file="progress.json"):
        self.carteira_esperada = carteira_esperada
        self.progress_file = progress_file

        self.db = MongoDBManager()

        try:
            self.attempted_combinations = set(
                obj['combination'] for obj in tqdm(self.db.load_objects(), 
                                                   desc="Carregando combinações tentadas", 
                                                   unit=" registros", leave=True)
            )
        except Exception as e:
            print("Error carregar combinações", e)
        
    def process_combination_sequence(self, combo, insert_progress, threads_progress, futures):
        try:
            seed = Bip39SeedGenerator(combo).Generate()
            bip44 = Bip44.FromSeed(seed, Bip44Coins.BITCOIN).DeriveDefaultPath()
            address = bip44.PublicKey().ToAddress()
            
            try:
                self.db.log_attempt(combo, address, 'not found', False, 'insert')

                # Atualiza progresso de inserção
                insert_progress.update(1)

                # Atualiza progresso das threads ativas
                futures.discard(combo)  # Remove a combinação concluída do conjunto
                threads_progress.n = len(futures)
                threads_progress.refresh()

                return True
            except Exception as e:
                print("Combinação duplicada", combo)


        except Exception as e:
            self.db.log_attempt(combo, 'Bip39SeedGenerator', 'error', None, 'insert')
            return False

    def generate_combinations(self, words, num_words, num_threads, type_gen):
        total_combinations = itertools.combinations(words, num_words)
        insert_progress = tqdm(desc="Gerando seeds", unit=" seeds", position=2)
        mnemo = Mnemonic("portuguese")
        # Inicializa a barra de progresso das threads ativas
        threads_progress = tqdm(desc="Threads em execução", position=0)

        try:
            combinations_progress = tqdm(desc="Gerando combinações aleatórias", unit=" frases", position=1)
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = set()

                try:
                    for combo in total_combinations:
                        combinations_progress.update(1)
                        combo_str = ' '.join(combo)
                        
                        if combo_str not in self.attempted_combinations and mnemo.check(combo_str):
                            self.attempted_combinations.add(combo_str)

                            futures.add(combo_str)
                            
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
    palavras = load_words_file(arquivo_lista_palavras)

    # "1CrmJ6RqsXrdHP7QYskX18cJSVJ8z6kE58"
    bf = BruteForceSeed()
    bf.generate_combinations(palavras, 12, 4, None)
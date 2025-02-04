# mongodb_manager.py
from pymongo import MongoClient


MONGO_URI = "mongodb://localhost:27017/"  # Altere para o URI do seu MongoDB
DB_NAME = "bip_39"
COLLECTION_NAME = "bip39_attempts"

class MongoDBManager:
    def __init__(self, mongo_uri=MONGO_URI, db_name=DB_NAME, collection_name=COLLECTION_NAME):
        """
        Inicializa a conexão com o MongoDB.
        :param mongo_uri: URI de conexão com o MongoDB.
        :param db_name: Nome do banco de dados.
        :param collection_name: Nome da coleção.
        """
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self._create_index()

    def _create_index(self):
        """
        Cria um índice único na coluna `combination` para melhorar o desempenho.
        """
        self.collection.create_index("combination", unique=True)

    def is_combination_processed(self, combo_str):
        """
        Verifica se uma combinação já foi processada.
        :param combo_str: Combinação de palavras.
        :return: True se a combinação já foi processada, False caso contrário.
        """
        return self.collection.find_one({"combination": combo_str}) is not None
    
    def load_objects(self):
         try:
            return list(self.collection.find({}, {"_id": 0}))
         except Exception as e:
             print("Error load objects", e)
    
    def log_attempt(self, phrase, btc_address, status, is_verified, type_op):
        try:
            if type_op == 'insert':
                self.collection.insert_one({
                    "combination": phrase,
                    "address": btc_address,
                    "status": status,
                    "is_verified": is_verified,
                })
            elif type_op == 'update':
                self.collection.update_one(
                    {"combination": phrase, "address": btc_address},  # Filter
                    {"$set": {"status": status, "is_verified": is_verified}}  # Update
                )
        except Exception as e:
            print("ocorreu um error", e)

    def save_combination(self, combo_str):
        """
        Salva uma combinação no banco de dados.
        :param combo_str: Combinação de palavras.
        """
        self.collection.update_one(
            {"combination": combo_str},
            {"$setOnInsert": {"combination": combo_str}},
            upsert=True
        )

    def close_connection(self):
        """
        Fecha a conexão com o MongoDB.
        """
        self.client.close()
class Rules:

    @staticmethod
    def add(data: dict, client: object, database: str, collection: str) -> str:
        return str(client[database][collection].insert_one(data).inserted_id)
    
    @staticmethod
    def get(query: dict, client: object, database: str, collection: str) -> dict:
        return client[database][collection].find_one(query)
    
    @staticmethod
    def get_all(query: dict, client: object, database: str, collection: str) -> list:
        return list(client[database][collection].find(query))

    @staticmethod
    def update(query: dict, data: dict, client: object, database: str, collection: str) -> dict:
        return client[database][collection].update_one(query, {'$set': data})
    
    @staticmethod
    def delete(query: dict, client: object, database: str, collection: str) -> dict:
        return client[database][collection].delete_one(query)
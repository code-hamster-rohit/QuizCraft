class Rules:

    @staticmethod
    def add(data: dict, client: object, database: str, collection: str) -> str:
        return str(client[database][collection].insert_one(data).inserted_id)
    
    @staticmethod
    def get(data: dict, client: object, database: str, collection: str) -> dict:
        return client[database][collection].find_one(data)

    @staticmethod
    def update(query: dict, data: dict, client: object, database: str, collection: str) -> dict:
        return client[database][collection].update_one(query, {'$set': data})
    
    @staticmethod
    def delete(query: dict, client: object, database: str, collection: str) -> dict:
        return client[database][collection].delete_one(query)
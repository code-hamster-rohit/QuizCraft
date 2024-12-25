
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    def __init__(self):
        self.__uri = f"mongodb+srv://{os.getenv('MDB_USERNAME')}:{os.getenv('MDB_PASSWORD')}@quizzer.igwb5.mongodb.net/?retryWrites=true&w=majority&appName=QUIZZER"
        self.__SetConnection()
    
    def __SetConnection(self):
        self.__client = MongoClient(self.__uri, server_api=ServerApi('1'))

    def GetClient(self):
        return self.__client
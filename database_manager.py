"""
Database Module
Handles MongoDB operations for SearchCRT
"""

import pymongo
from pymongo import MongoClient
from config_manager import config_manager
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            config = config_manager.get_database_config()
            
            connection_string = f"mongodb://{config['host']}:{config['port']}"
            
            if config['username']:
                connection_string = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}"
            
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            self.db = self.client[config['database']]
            
            # Test connection
            self.client.server_info()
            logger.info("Connected to MongoDB successfully")
            
        except pymongo.errors.ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def get_collection(self, collection_name):
        """Get a collection from the database"""
        if self.db is None:
            raise RuntimeError("Database not connected")
        return self.db[collection_name]
    
    def insert_search(self, search_data):
        """Insert a search record"""
        try:
            collection = self.get_collection(config_manager.get('Database', 'collection_searches', 'searches'))
            result = collection.insert_one(search_data)
            logger.info(f"Search record inserted: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error inserting search: {e}")
            raise
    
    def insert_result(self, result_data):
        """Insert a result record"""
        try:
            collection = self.get_collection(config_manager.get('Database', 'collection_results', 'results'))
            result = collection.insert_one(result_data)
            logger.info(f"Result record inserted: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error inserting result: {e}")
            raise
    
    def get_search_history(self, limit=100):
        """Get search history"""
        try:
            collection = self.get_collection(config_manager.get('Database', 'collection_searches', 'searches'))
            searches = list(collection.find().sort('_id', -1).limit(limit))
            return searches
        except Exception as e:
            logger.error(f"Error retrieving search history: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")

# Global database instance
db_manager = None

def get_db_manager():
    global db_manager
    if db_manager is None:
        try:
            db_manager = DatabaseManager()
        except Exception as e:
            logger.warning(f"Database connection failed: {e}. Operating in offline mode.")
    return db_manager

"""
db.py
─────
Handles the MongoDB Atlas connection using PyMongo.
The connection is lazy: it's created once when first needed.
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

_client = None  # Module-level singleton


def get_db():
    """
    Returns the quiz database instance.
    Creates the MongoClient only once (singleton pattern).
    """
    global _client

    if _client is None:
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            raise ValueError("MONGO_URI is not set in your .env file!")
        _client = MongoClient(mongo_uri)

    db_name = os.getenv("MONGO_DBNAME", "quizdb")
    return _client[db_name]

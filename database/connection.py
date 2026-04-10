import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConfigurationError, ConnectionFailure, InvalidURI, OperationFailure


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

_client: Optional[MongoClient] = None


def get_client() -> Optional[MongoClient]:
    global _client
    if _client is not None:
        return _client

    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        return None

    try:
        _client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
        _client.admin.command("ping")
        return _client
    except (ConfigurationError, ConnectionFailure, InvalidURI, OperationFailure):
        return None


def get_database() -> Optional[Database]:
    client = get_client()
    if client is None:
        return None
    return client[os.getenv("MONGO_DB_NAME", "grocery_admin")]

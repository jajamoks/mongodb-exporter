import pymongo
import json
import os
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv
import sys

load_dotenv()


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle MongoDB ObjectId and other BSON types"""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()

        return super(JSONEncoder, self).default(obj)

def export_mongodb_database(connection_string, database_name, output_directory="mongodb_export"):
    """Export a MongoDB database to a directory of JSON files"""

    try:
        client = pymongo.MongoClient(connection_string)
        db = client[database_name]
        full_output_directory = os.path.join(output_directory, database_name)

        if not os.path.exists(full_output_directory):
            os.makedirs(full_output_directory)

        collections = db.list_collection_names()

        print(f"Exporting database: {database_name}")
        print(f"Found {len(collections)} collections")

        for collection_name in collections:
            collection = db[collection_name]
            documents = list(collection.find())

            file_name = f"{database_name}/{collection_name}.json"
            file_path = os.path.join(output_directory, file_name)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(documents, f, cls=JSONEncoder, indent=2, ensure_ascii=False)

            print(f"Exported {len(documents)} documents to {file_path}")
        
        print(f"Database {database_name} exported successfully")
        client.close()
        return True
        
    except Exception as e:
        print(f"Error during export: {str(e)}")
        return False


if __name__ == "__main__":
    CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
    DATABASE_NAME = os.getenv("DATABASE_NAME")  
    
    success = export_mongodb_database(CONNECTION_STRING, DATABASE_NAME)
    if success:
        print("Export completed successfully!")
    else:
        print("Export failed!")
        sys.exit(1)


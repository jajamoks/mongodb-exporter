import os
import json
import pymongo
from dotenv import load_dotenv
import sys
from datetime import datetime
from bson import ObjectId

load_dotenv()

def import_mongodb_database(connection_string, source_database_name, target_database_name, input_directory="mongodb_export"):
    """Import JSON files from a directory into a MongoDB database"""
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(connection_string)
        
        # Create/connect to target database
        target_db = client[target_database_name]
        
        # Construct the source directory path
        source_directory = os.path.join(input_directory, source_database_name)
        
        if not os.path.exists(source_directory):
            print(f"Source directory not found: {source_directory}")
            return False
        
        # Get all JSON files in the source directory
        json_files = [f for f in os.listdir(source_directory) if f.endswith('.json')]
        
        if not json_files:
            print(f"No JSON files found in {source_directory}")
            return False
        
        total_documents = 0
        
        for json_file in json_files:
            collection_name = json_file.replace('.json', '')
            print(f"Processing: {json_file}")
            file_path = os.path.join(source_directory, json_file)
            
            # Read JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            if not documents:
                print(f"No documents in {json_file}")
                continue
            
            # Get target collection
            collection = target_db[collection_name]
            
            # Insert documents
            if isinstance(documents, list):
                if documents:  # Only insert if list is not empty
                    result = collection.insert_many(documents)
                    inserted_count = len(result.inserted_ids)
                    print(f"  ✅ Inserted {inserted_count} documents into {collection_name}")
                    total_documents += inserted_count
            else:
                # Single document
                result = collection.insert_one(documents)
                print(f"  ✅ Inserted 1 document into {collection_name}")
                total_documents += 1

        print(f"🎉 Import completed successfully!")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"Error during import: {str(e)}")
        return False

if __name__ == "__main__":
    # Get connection details from environment
    CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
    SOURCE_DATABASE_NAME = os.getenv("DATABASE_NAME")
    TARGET_DATABASE_NAME = os.getenv("TARGET_DATABASE_NAME")

    if not CONNECTION_STRING or not SOURCE_DATABASE_NAME or not TARGET_DATABASE_NAME:
        print("Error: Missing required environment variables")
        print("Please check your .env file has:")
        print("  - MONGODB_CONNECTION_STRING")
        print("  - SOURCE_DATABASE_NAME")
        print("  - TARGET_DATABASE_NAME")
        sys.exit(1)

    # Run the import
    success = import_mongodb_database(CONNECTION_STRING, SOURCE_DATABASE_NAME, TARGET_DATABASE_NAME)
    
    if success:
        print("✅ Import completed successfully!")
    else:
        print("Import failed!")
        sys.exit(1)

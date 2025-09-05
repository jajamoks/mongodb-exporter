import os
import pymongo
from dotenv import load_dotenv
import sys

load_dotenv()

def drop_mongodb_database(connection_string, database_name, confirm=False):
    """Drop a MongoDB database with extra safety confirmations"""
    
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(connection_string)
        
        # Check if database exists
        if database_name not in client.list_database_names():
            print(f"❌ Database '{database_name}' does not exist")
            client.close()
            return False
        
        # Get database info before dropping
        db = client[database_name]
        collections = db.list_collection_names()
        
        print(f"🗑️  Database to drop: {database_name}")
        print(f"📊 Collections in database: {len(collections)}")
        
        if collections:
            print("�� Collections:")
            for collection_name in collections:
                count = db[collection_name].count_documents({})
                print(f"  - {collection_name}: {count} documents")
        
        # Extra safety confirmations
        if not confirm:
            print("\n" + "="*60)
            print("⚠️  CRITICAL WARNING: DATABASE DELETION")
            print("="*60)
            print("This operation will PERMANENTLY DELETE:")
            print(f"  • Database: {database_name}")
            print(f"  • Collections: {len(collections)}")
            print(f"  • All data and indexes")
            print("  • This action CANNOT be undone!")
            print("="*60)
            
            # First confirmation
            response1 = input(f"\n🔴 Are you absolutely sure you want to drop database '{database_name}'? (yes/no): ").lower().strip()
            
            if response1 not in ['yes', 'y']:
                print("❌ Operation cancelled")
                client.close()
                return False
            
            # Second confirmation with database name
            print(f"\n🔴 FINAL CONFIRMATION:")
            print(f"Type the exact database name '{database_name}' to confirm deletion:")
            response2 = input("Database name: ").strip()
            
            if response2 != database_name:
                print(f"❌ Database name mismatch. Expected '{database_name}', got '{response2}'")
                print("❌ Operation cancelled for safety")
                client.close()
                return False
            
            # Third confirmation
            response3 = input(f"\n🔴 Last chance! Type 'DELETE' to permanently drop '{database_name}': ").strip()
            
            if response3 != 'DELETE':
                print("❌ Confirmation failed. Operation cancelled")
                client.close()
                return False
        
        # Drop the database
        print(f"\n🗑️  Dropping database '{database_name}'...")
        client.drop_database(database_name)
        
        # Verify it was dropped
        if database_name not in client.list_database_names():
            print(f"✅ Database '{database_name}' successfully dropped")
            client.close()
            return True
        else:
            print(f"❌ Failed to drop database '{database_name}'")
            client.close()
            return False
        
    except Exception as e:
        print(f"❌ Error dropping database: {str(e)}")
        return False

def list_databases(connection_string):
    """List all databases in MongoDB"""
    
    try:
        client = pymongo.MongoClient(connection_string)
        databases = client.list_database_names()
        
        print("📋 Available databases:")
        print("-" * 30)
        
        for db_name in databases:
            # Skip system databases
            if db_name in ['admin', 'local', 'config']:
                continue
                
            db = client[db_name]
            collections = db.list_collection_names()
            total_docs = 0
            
            for collection in collections:
                total_docs += db[collection].count_documents({})
            
            print(f"📊 {db_name}: {len(collections)} collections, {total_docs} documents")
        
        client.close()
        return databases
        
    except Exception as e:
        print(f"❌ Error listing databases: {str(e)}")
        return []

if __name__ == "__main__":
    # Get connection details from environment
    CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
    
    if not CONNECTION_STRING:
        print("❌ Error: Missing MONGODB_CONNECTION_STRING in .env file")
        sys.exit(1)
    
    print(f"🔗 Connection: {CONNECTION_STRING}")
    print("-" * 50)
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 mongodb_drop.py list                    # List all databases")
        print("  python3 mongodb_drop.py drop                    # Drop database (will ask for name)")
        print("  python3 mongodb_drop.py force                   # Force drop database (will ask for name)")
        print("  python3 mongodb_drop.py drop <database_name>    # Drop specific database")
        print("  python3 mongodb_drop.py force <database_name>   # Force drop specific database")
        print("\nExamples:")
        print("  python3 mongodb_drop.py list")
        print("  python3 mongodb_drop.py drop")
        print("  python3 mongodb_drop.py force")
        print("  python3 mongodb_drop.py drop test_database")
        print("  python3 mongodb_drop.py force backup_2024")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "list":
        print("📋 Listing all databases...")
        databases = list_databases(CONNECTION_STRING)
        
    elif command == "drop":
        # Get database name from command line or ask user
        if len(sys.argv) >= 3:
            database_name = sys.argv[2]
        else:
            # Ask user for database name
            database_name = input("Enter database name to drop: ").strip()
            if not database_name:
                print("❌ No database name provided")
                sys.exit(1)
        
        print(f"🗑️  Dropping database: {database_name}")
        success = drop_mongodb_database(CONNECTION_STRING, database_name, confirm=False)
        
        if success:
            print("✅ Database dropped successfully!")
        else:
            print("❌ Failed to drop database!")
            sys.exit(1)
    
    elif command == "force":
        # Get database name from command line or ask user
        if len(sys.argv) >= 3:
            database_name = sys.argv[2]
        else:
            # Ask user for database name
            database_name = input("Enter database name to drop: ").strip()
            if not database_name:
                print("❌ No database name provided")
                sys.exit(1)
        
        print(f"🗑️  Force dropping database: {database_name}")
        success = drop_mongodb_database(CONNECTION_STRING, database_name, confirm=True)
        
        if success:
            print("✅ Database dropped successfully!")
        else:
            print("❌ Failed to drop database!")
            sys.exit(1)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: list, drop, force")
        sys.exit(1)

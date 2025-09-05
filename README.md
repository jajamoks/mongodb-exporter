# MongoDB Exporter & Importer

A simple Python script to export MongoDB databases to JSON files and import them back into new databases.

## Features

- **Export**: Export entire MongoDB databases to JSON files
- **Import**: Import JSON files back into new MongoDB databases
- Handles MongoDB ObjectId and DateTime serialization
- Creates separate JSON files for each collection
- Command-line interface for easy usage
- Environment variable configuration support
- SSL/TLS support for MongoDB Atlas

## Prerequisites

- Python 3.6 or higher
- MongoDB instance (local or remote/Atlas)
- Access to the MongoDB database you want to export/import

## Installation

1. **Clone or download this repository**
   ```bash
   git clone <your-repo-url>
   cd mongodb-exporter
   ```

2. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip3 install pymongo python-dotenv
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

4. **Edit the `.env` file with your MongoDB connection details:**
   ```bash
   nano .env
   ```

## Configuration

### Environment Variables (.env file)

```bash
# MongoDB connection string
MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority&appName=cluster0&tlsAllowInvalidCertificates=true

# Source database name (for export)
DATABASE_NAME=your_database_name

# Output directory for exported files (optional, defaults to 'mongodb_export')
OUTPUT_DIRECTORY=mongodb_export
```

### Connection String Examples

#### Local MongoDB
```
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
```

#### Local MongoDB with Authentication
```
MONGODB_CONNECTION_STRING=mongodb://username:password@localhost:27017
```

#### MongoDB Atlas
```
MONGODB_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority&appName=cluster0&tlsAllowInvalidCertificates=true
```

## Usage

### 🔄 Export Database

Export your MongoDB database to JSON files:

#### Method 1: Using Environment Variables (Recommended)
```bash
python3 mongodb_export.py
```

#### Method 2: Command Line Arguments
```bash
python3 mongodb_export.py "<connection_string>" "<database_name>"
```

**Examples:**
```bash
# Local MongoDB
python3 mongodb_export.py "mongodb://localhost:27017" "my_database"

# MongoDB Atlas
python3 mongodb_export.py "mongodb+srv://user:pass@cluster.mongodb.net/" "my_database"
```

### 📥 Import Database

Import JSON files into a new MongoDB database:

#### Method 1: Auto-generated Target Database Name
```bash
python3 mongodb_import.py
```
This creates a database named `{source_database_name}_imported`

#### Method 2: Custom Target Database Name
```bash
python3 mongodb_import.py "your_new_database_name"
```

**Examples:**
```bash
# Import to "my_backup_database"
python3 mongodb_import.py "my_backup_database"

# Import to "test_environment"
python3 mongodb_import.py "test_environment"

# Import to "production_backup_2024"
python3 mongodb_import.py "production_backup_2024"
```

## Complete Workflow Example

### 1. Export Your Database
```bash
# Make sure your .env file is configured
python3 mongodb_export.py
```

**Output:**
```
Exporting database: my_database
Found 5 collections
Exported 100 documents to mongodb_export/my_database/users.json
Exported 250 documents to mongodb_export/my_database/products.json
Exported 50 documents to mongodb_export/my_database/orders.json
Exported 10 documents to mongodb_export/my_database/categories.json
Exported 5 documents to mongodb_export/my_database/settings.json
Database my_database exported successfully
Export completed successfully!
```

### 2. Import to New Database
```bash
# Import to a new database called "backup_2024"
python3 mongodb_import.py "backup_2024"
```

**Output:**
```
🔗 Connection: mongodb+srv://user:pass@cluster.mongodb.net/
📂 Source database: my_database
🎯 Target database: backup_2024
--------------------------------------------------
📁 Importing from: mongodb_export/my_database
📊 Found 5 JSON files to import
--------------------------------------------------
📄 Processing: users.json
  ✅ Inserted 100 documents into users
�� Processing: products.json
  ✅ Inserted 250 documents into products
📄 Processing: orders.json
  ✅ Inserted 50 documents into orders
📄 Processing: categories.json
  ✅ Inserted 10 documents into categories
📄 Processing: settings.json
  ✅ Inserted 5 documents into settings
--------------------------------------------------
🎉 Import completed successfully!
📊 Total documents imported: 415
🎯 Target database: backup_2024
✅ Import completed successfully!
```

## File Structure

After export, your directory will look like:
```
mongodb-exporter/
├── mongodb_export.py          # Export script
├── mongodb_import.py          # Import script
├── requirements.txt           # Python dependencies
├── .env                      # Your configuration (not in git)
├── .env.example              # Configuration template
├── README.md                 # This file
└── mongodb_export/           # Export output directory
    └── your_database_name/   # Database-specific folder
        ├── users.json
        ├── products.json
        ├── orders.json
        └── ...
```

## Testing Your Connection

Before running export/import, test your MongoDB connection:

```bash
python3 -c "
import os
from dotenv import load_dotenv
import pymongo

load_dotenv()
connection_string = os.getenv('MONGODB_CONNECTION_STRING')
database_name = os.getenv('DATABASE_NAME')

print(f'🔗 Testing connection to: {database_name}')
try:
    client = pymongo.MongoClient(connection_string)
    client.admin.command('ping')
    print('✅ Connection successful!')
    
    # List collections
    db = client[database_name]
    collections = db.list_collection_names()
    print(f'📊 Found {len(collections)} collections:')
    for collection in collections:
        count = db[collection].count_documents({})
        print(f'  - {collection}: {count} documents')
    
    client.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

## Troubleshooting

### Common Issues

#### 1. Connection Refused
- Make sure MongoDB is running
- Check if the port (default: 27017) is correct
- Verify firewall settings

#### 2. Authentication Failed
- Check username and password in connection string
- Ensure the user has read/write permissions on the database

#### 3. SSL Certificate Errors (Atlas)
- Add `&tlsAllowInvalidCertificates=true` to your connection string
- This is already included in the example Atlas connection string

#### 4. Import Errors
- Make sure you have exported data first
- Check that the export directory exists
- Verify JSON files are not corrupted

#### 5. Permission Errors
- Ensure you have write permissions in the output directory
- Check MongoDB user permissions for import operations

### Debug Mode

Add debug output by modifying the scripts to include more verbose logging:

```python
# Add this to see more details
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Notes

- Never commit `.env` files with real credentials
- Use environment variables for production deployments
- Consider using MongoDB's built-in authentication and authorization
- For production, use connection string with SSL/TLS
- The `tlsAllowInvalidCertificates=true` parameter is for development only

## Use Cases

### Database Backup
```bash
# Export production database
python3 mongodb_export.py

# Import to backup database
python3 mongodb_import.py "production_backup_$(date +%Y%m%d)"
```

### Environment Migration
```bash
# Export from development
python3 mongodb_export.py

# Import to staging
python3 mongodb_import.py "staging_environment"
```

### Data Analysis
```bash
# Export for analysis
python3 mongodb_export.py

# Import to analysis database
python3 mongodb_import.py "analysis_database"
```

## License

This project is open source and available under the MIT License.

#!/usr/bin/env python3
import os
import sys
import sqlite3

# Add the parent directory to Python path to find the app package
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

def init_database():
    """Initialize database with schema in db/sqlitedb directory"""
    print("Initializing database schema...")
    
    # Database path should be in db/sqlitedb/whatsapp_platform.db
    db_path = os.path.join(parent_dir, 'db/sqlitedb/whatsapp_platform.db')
    
    # Ensure the sqlitedb directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    print(f"Database path: {db_path}")
    
    try:
        # Create database connection directly (without Flask context)
        db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        db.row_factory = sqlite3.Row
        
        # Enable foreign keys
        db.execute("PRAGMA foreign_keys = ON")
        
        # Read and execute the schema
        schema_path = os.path.join(parent_dir, 'db/scripts/schema-sqlite.sql')
        
        if not os.path.exists(schema_path):
            print(f"ERROR: Schema file not found: {schema_path}")
            return False
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute the schema
        db.executescript(schema_sql)
        db.commit()
        print("SUCCESS: Database schema initialized successfully!")
        
        # Verify tables were created
        tables = ['users', 'topics', 'templates', 'segments', 'campaigns', 'messages', 'events_inbound', 'delivery_receipts']
        success_count = 0
        
        for table in tables:
            result = db.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
            if result:
                print(f"SUCCESS: Table '{table}' created successfully")
                success_count += 1
            else:
                print(f"ERROR: Table '{table}' missing!")
        
        print(f"Tables created: {success_count}/{len(tables)}")
        
        # Show table counts
        print("Table record counts:")
        for table in tables:
            try:
                count = db.execute(f"SELECT COUNT(*) as cnt FROM {table}").fetchone()['cnt']
                print(f"   {table}: {count} records")
            except Exception as e:
                print(f"   {table}: Error - {e}")
        
        db.close()
        return success_count == len(tables)
        
    except Exception as e:
        print(f"ERROR: Error initializing database: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    if success:
        print("Database initialization completed successfully!")
        sys.exit(0)
    else:
        print("Database initialization failed!")
        sys.exit(1)
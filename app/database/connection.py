import sqlite3
import os
from flask import g, current_app

def get_db():
    """Get database connection"""
    if 'db' not in g:
        # Use the path from Flask app config or default to db/sqlitedb/whatsapp_platform.db
        db_path = current_app.config.get('DATABASE_PATH', 'db/sqlitedb/whatsapp_platform.db')
        
        # If it's a relative path, make it absolute relative to project root
        if not os.path.isabs(db_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, db_path)
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        g.db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        # Enable foreign keys
        g.db.execute("PRAGMA foreign_keys = ON")
        
        # Check if tables exist and initialize if needed
        _ensure_tables_exist(g.db, db_path)
    
    return g.db

def _ensure_tables_exist(db, db_path):
    """Ensure all required tables exist, create them if missing"""
    required_tables = ['users', 'topics', 'templates', 'segments', 'campaigns', 'messages', 'events_inbound', 'delivery_receipts']
    
    missing_tables = []
    for table in required_tables:
        result = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
        if not result:
            missing_tables.append(table)
    
    if missing_tables:
        print(f"WARNING: Missing tables detected: {missing_tables}")
        print("Initializing database schema...")
        
        # Get the schema path
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        schema_path = os.path.join(base_dir, 'db/scripts/schema-sqlite.sql')
        
        if os.path.exists(schema_path):
            try:
                with open(schema_path, 'r') as f:
                    schema_sql = f.read()
                
                # Execute the schema
                db.executescript(schema_sql)
                db.commit()
                print("SUCCESS: Database schema initialized successfully!")
                
                # Verify tables were created
                for table in missing_tables:
                    result = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone()
                    if result:
                        print(f"SUCCESS: Table '{table}' created")
                    else:
                        print(f"ERROR: Failed to create table '{table}'")
                        
            except Exception as e:
                print(f"ERROR: Error initializing database schema: {e}")
        else:
            print(f"ERROR: Schema file not found at: {schema_path}")

def close_db(e=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """Initialize database with app"""
    app.teardown_appcontext(close_db)
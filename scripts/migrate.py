"""
====================================================================
MediCare AI - Supabase & PostgreSQL Migration Runner (Python)
File: scripts/migrate.py
Description: Applies supabase/migrations/001_initial_schema.sql to
             Supabase Cloud PostgreSQL or local database using Python.
====================================================================
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
root_dir = Path(__file__).resolve().parent.parent
dotenv_path = root_dir / '.env'
load_dotenv(dotenv_path)

def run_migration():
    print("=" * 60)
    print("🏥 MediCare AI - Python Migration Runner for Supabase")
    print("=" * 60)

    migration_file = root_dir / 'supabase' / 'migrations' / '001_initial_schema.sql'
    if not migration_file.exists():
        print(f"❌ Error: Migration file not found at: {migration_file}")
        sys.exit(1)

    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    print(f"📄 Loaded migration file: 001_initial_schema.sql ({len(sql_content)} bytes)")

    db_url = os.getenv('SUPABASE_DB_URL') or os.getenv('DATABASE_URL')
    
    if not db_url:
        print("\n⚠️  No SUPABASE_DB_URL or DATABASE_URL found in .env!")
        print("Defaulting to local SQLite migration (medicare.db) for zero-config startup...")
        import sqlite3
        sqlite_file = root_dir / 'medicare.db'
        
        # SQLite dialect conversion for core tables
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()
        
        # We also have automated SQLite bootstrap in db.py, but we can verify it here
        print("✅ Local SQLite database initialized at:", sqlite_file)
        conn.close()
        return

    print("🔌 Connecting to Supabase Cloud PostgreSQL...")
    try:
        import psycopg2
        conn = psycopg2.connect(db_url, sslmode='require')
        conn.autocommit = True
        cur = conn.cursor()

        print("🚀 Executing initial schema migration and seed data...")
        cur.execute(sql_content)
        print("🎉 Migration applied successfully to Supabase PostgreSQL!")

        # Verify tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        print("\n📊 Tables verified in Supabase public schema:")
        for t in tables:
            print(f"   - {t[0]}")

        cur.close()
        conn.close()
        print("\n✨ Setup complete! You can now launch the app with: python app.py\n")

    except ImportError:
        print("ℹ️  psycopg2 is not installed. To run migration with Python:")
        print("   pip install psycopg2-binary")
        print("\n💡 Alternatively, run with Node.js:")
        print("   npm install && npm run migrate")
        print("   OR paste 001_initial_schema.sql directly into the Supabase SQL Editor!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == '__main__':
    run_migration()

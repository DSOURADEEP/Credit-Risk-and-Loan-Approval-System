#!/usr/bin/env python3
"""
Database setup script for Credit Risk & Loan Approval System
"""

import mysql.connector
from mysql.connector import Error
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.config import settings

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect without specifying database
        connection = mysql.connector.connect(
            host=settings.DATABASE_HOST,
            port=settings.DATABASE_PORT,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD
        )
        
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.DATABASE_NAME}")
        cursor.execute(f"USE {settings.DATABASE_NAME}")
        
        print(f"Database '{settings.DATABASE_NAME}' created/verified successfully")
        
        return connection, cursor
        
    except Error as e:
        print(f"Error creating database: {e}")
        sys.exit(1)

def execute_sql_file(cursor, file_path: str):
    """Execute SQL commands from a file"""
    try:
        with open(file_path, 'r') as file:
            sql_content = file.read()
            
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement:
                cursor.execute(statement)
        
        print(f"Successfully executed SQL file: {file_path}")
        
    except Error as e:
        print(f"Error executing SQL file {file_path}: {e}")
        raise
    except FileNotFoundError:
        print(f"SQL file not found: {file_path}")
        raise

def main():
    """Main setup function"""
    print("Setting up Credit Risk & Loan Approval System database...")
    
    # Create database connection
    connection, cursor = create_database()
    
    try:
        # Get the directory containing this script
        script_dir = Path(__file__).parent
        database_dir = script_dir.parent / "database"
        
        # Execute schema creation
        schema_file = database_dir / "schema.sql"
        if schema_file.exists():
            execute_sql_file(cursor, str(schema_file))
        else:
            print(f"Schema file not found: {schema_file}")
            return
        
        # Execute seed data
        seed_file = database_dir / "seed_data.sql"
        if seed_file.exists():
            execute_sql_file(cursor, str(seed_file))
        else:
            print(f"Seed data file not found: {seed_file}")
        
        connection.commit()
        print("Database setup completed successfully!")
        
    except Exception as e:
        connection.rollback()
        print(f"Database setup failed: {e}")
        sys.exit(1)
        
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()
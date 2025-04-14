#!/usr/bin/env python3
"""
Database initialization and connection script.

This script initializes the database connection and provides utility functions
for working with the database.
"""

import os
import sys
import logging
from typing import Dict, List, Optional, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Database connection parameters
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'gdpr_fines'),
    'user': os.getenv('DB_USER', 'andi_user'),
    'password': os.getenv('DB_PASSWORD', 'andi_password')
}

def get_connection():
    """
    Create a connection to the PostgreSQL database.
    
    Returns:
        psycopg2.connection: A database connection object
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info(f"Successfully connected to database {DB_CONFIG['database']} on {DB_CONFIG['host']}")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to the database: {e}")
        raise

def execute_query(query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Execute a query and return the results as a list of dictionaries.
    
    Args:
        query: SQL query to execute
        params: Parameters for the query
        
    Returns:
        List of dictionaries representing the query results
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if cur.description:
                results = cur.fetchall()
                return [dict(row) for row in results]
            return []
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise
    finally:
        if conn:
            conn.close()

def execute_transaction(queries: List[Dict[str, Any]]) -> bool:
    """
    Execute multiple queries in a transaction.
    
    Args:
        queries: List of dictionaries with 'query' and 'params' keys
        
    Returns:
        True if successful, False otherwise
    """
    conn = None
    try:
        conn = get_connection()
        with conn:  # Transaction block
            with conn.cursor() as cur:
                for item in queries:
                    cur.execute(item['query'], item.get('params', None))
        return True
    except Exception as e:
        logger.error(f"Error executing transaction: {e}")
        return False
    finally:
        if conn:
            conn.close()

def check_connection():
    """Check if the database connection is working."""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
            assert result[0] == 1
            logger.info("Database connection check successful")
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False

def main():
    """Main function to test the database connection."""
    if check_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
        
if __name__ == "__main__":
    main() 
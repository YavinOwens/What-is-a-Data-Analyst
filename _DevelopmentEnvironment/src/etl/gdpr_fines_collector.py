#!/usr/bin/env python3
"""
GDPR Fines Collector

This script collects GDPR fines data from external sources, validates it,
and loads it into the database.
"""

import os
import sys
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

import pandas as pd
import requests
from requests.exceptions import RequestException
from sqlalchemy import create_engine, text

# Add parent directory to path to allow importing from sibling modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.init_db import DB_CONFIG, check_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Database connection string
db_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

class GDPRFinesCollector:
    """Collects and processes GDPR fines data."""
    
    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the GDPR fines collector.
        
        Args:
            api_url: URL for the GDPR fines API
            api_key: API key for authentication
        """
        self.api_url = api_url or os.getenv('API_BASE_URL', 'https://api.example.com')
        self.api_key = api_key or os.getenv('API_KEY', '')
        self.engine = create_engine(db_url)
        
        # For demo purposes, we'll use a sample file if available
        self.sample_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            '../../data/sample_gdpr_fines.json'
        )
        
    def fetch_data(self) -> List[Dict[str, Any]]:
        """
        Fetch GDPR fines data from the API or sample file.
        
        Returns:
            List of GDPR fines data
        """
        try:
            # Try to fetch from API first
            headers = {'Authorization': f'Bearer {self.api_key}'} if self.api_key else {}
            response = requests.get(f"{self.api_url}/fines", headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except (RequestException, json.JSONDecodeError) as e:
            logger.warning(f"Failed to fetch data from API: {e}")
            
            # Fall back to sample file for demo purposes
            if os.path.exists(self.sample_file):
                logger.info(f"Using sample data from {self.sample_file}")
                with open(self.sample_file, 'r') as f:
                    return json.load(f)
            
            # Generate a minimal sample if no sample file
            logger.warning("No sample file found, generating minimal sample data")
            return self._generate_sample_data()
    
    def _generate_sample_data(self) -> List[Dict[str, Any]]:
        """
        Generate minimal sample data for demo purposes.
        
        Returns:
            List of sample GDPR fines data
        """
        return [
            {
                "country": "Germany",
                "authority": "BfDI",
                "company": "Deutsche Wohnen SE",
                "amount": 14500000,
                "date": "2019-10-30",
                "article_violated": "Art. 5 GDPR",
                "type_of_violation": "Insufficient legal basis for data processing",
                "summary": "Fine for storing personal data longer than necessary."
            },
            {
                "country": "France",
                "authority": "CNIL",
                "company": "Google LLC",
                "amount": 50000000,
                "date": "2019-01-21",
                "article_violated": "Art. 6, 12-14 GDPR",
                "type_of_violation": "Lack of transparency",
                "summary": "Fine for lack of transparency and valid consent."
            }
        ]
    
    def validate_data(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Validate and clean the GDPR fines data.
        
        Args:
            data: Raw GDPR fines data
            
        Returns:
            DataFrame with validated data
        """
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Check required columns
        required_columns = ['country', 'company', 'amount', 'date']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Validate data types and formats
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Filter out invalid records
        invalid_amount = df['amount'].isna()
        invalid_date = df['date'].isna()
        
        if invalid_amount.any() or invalid_date.any():
            invalid_count = (invalid_amount | invalid_date).sum()
            logger.warning(f"Dropped {invalid_count} invalid records")
            df = df[~(invalid_amount | invalid_date)]
        
        return df
    
    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the GDPR fines data.
        
        Args:
            df: DataFrame with validated data
            
        Returns:
            DataFrame with transformed data
        """
        # Standardize column names
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        
        # Ensure date format is consistent
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date']).dt.date
        
        # Add processing timestamp
        df['created_at'] = datetime.now()
        df['updated_at'] = datetime.now()
        
        return df
    
    def load_data(self, df: pd.DataFrame) -> int:
        """
        Load the GDPR fines data into the database.
        
        Args:
            df: DataFrame with transformed data
            
        Returns:
            Number of records loaded
        """
        try:
            # Check if table exists, if not create schema and table first
            with self.engine.connect() as conn:
                conn.execute(text("CREATE SCHEMA IF NOT EXISTS gdpr"))
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS gdpr.fines (
                        id SERIAL PRIMARY KEY,
                        country VARCHAR(100) NOT NULL,
                        authority VARCHAR(200),
                        company VARCHAR(200) NOT NULL,
                        amount NUMERIC(20, 2) NOT NULL,
                        date DATE NOT NULL,
                        controller_processor VARCHAR(50),
                        article_violated VARCHAR(100),
                        type_of_violation TEXT,
                        source_url TEXT,
                        summary TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
                
            # Load data to database
            records_loaded = df.to_sql(
                'fines', 
                self.engine, 
                schema='gdpr',
                if_exists='append',
                index=False,
                method='multi'
            )
            
            logger.info(f"Successfully loaded {records_loaded} records")
            return records_loaded
        except Exception as e:
            logger.error(f"Error loading data to database: {e}")
            raise
    
    def run_etl(self) -> bool:
        """
        Run the full ETL process.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check database connection
            if not check_connection():
                raise RuntimeError("Database connection failed")
                
            # Extract
            logger.info("Fetching GDPR fines data...")
            raw_data = self.fetch_data()
            logger.info(f"Fetched {len(raw_data)} records")
            
            # Validate
            logger.info("Validating data...")
            validated_df = self.validate_data(raw_data)
            
            # Transform
            logger.info("Transforming data...")
            transformed_df = self.transform_data(validated_df)
            
            # Load
            logger.info("Loading data to database...")
            self.load_data(transformed_df)
            
            logger.info("ETL process completed successfully")
            return True
        except Exception as e:
            logger.error(f"ETL process failed: {e}")
            return False

def main():
    """
    Main function to run the ETL process.
    """
    collector = GDPRFinesCollector()
    success = collector.run_etl()
    
    if success:
        print("✅ ETL process completed successfully")
    else:
        print("❌ ETL process failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 
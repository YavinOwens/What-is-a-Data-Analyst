import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime
import json
import os
from typing import List, Dict, Any
import logging
import re
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GDPRScraper:
    def __init__(self):
        self.base_url = "https://www.enforcementtracker.com"
        self.data_dir = os.path.dirname(os.path.abspath(__file__))
        self.raw_data_file = os.path.join(self.data_dir, 'raw_gdpr_data.json')
        self.processed_data_file = os.path.join(self.data_dir, 'gdpr_enforcement_data.csv')

    async def scrape_page(self, page_num):
        logging.info(f"Scraping page {page_num}")
        
        # Wait for table to load
        await self.page.wait_for_selector('table.table')
        
        # Get the table HTML
        table_html = await self.page.inner_html('table.table')
        soup = BeautifulSoup(table_html, 'html.parser')
        
        # Find all rows except header
        rows = soup.find_all('tr')[1:]  # Skip header row
        fines = []
        
        for row in rows:
            fine = self.process_row(row)
            if fine:
                fines.append(fine)
                logging.info(f"Scraped fine: {fine['company']} - {fine['amount']}")
        
        return fines

    async def scrape_fines(self):
        fines = []
        max_pages = 10  # Only scrape first 10 pages
        
        for page in range(1, max_pages + 1):
            # Navigate to page
            if page > 1:
                await self.page.goto(f"{self.base_url}?page={page}")
                await asyncio.sleep(2)  # Small delay between pages
            
            page_fines = await self.scrape_page(page)
            fines.extend(page_fines)
            
            logging.info(f"Completed page {page}, found {len(page_fines)} fines")
        
        return fines

    def save_raw_data(self, data: List[Dict[str, Any]]):
        """Save raw scraped data to JSON file"""
        try:
            with open(self.raw_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Raw data saved to {self.raw_data_file}")
        except Exception as e:
            logger.error(f"Error saving raw data: {str(e)}")

    def process_and_save_data(self, data: List[Dict[str, Any]]):
        """Process and save data to CSV"""
        try:
            df = pd.DataFrame(data)
            
            # Convert date strings to datetime objects
            df['date'] = pd.to_datetime(df['date'].astype(str).str.slice(0, 8), format='%Y%m%d')
            
            # Clean amount column
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
            # Save to CSV
            df.to_csv(self.processed_data_file, index=False)
            logger.info(f"Processed data saved to {self.processed_data_file}")
            
            # Print basic statistics
            logger.info("\nData Quality Summary:")
            logger.info(f"Total fines: {len(df)}")
            logger.info(f"Total amount: EUR {df['amount'].sum():,.2f}")
            logger.info(f"Average fine: EUR {df['amount'].mean():,.2f}")
            logger.info(f"Countries: {df['country'].nunique()}")
            logger.info(f"Articles: {df['article'].nunique()}")
            
            # Print data quality metrics
            logger.info("\nData Quality Metrics:")
            logger.info("Missing dates: %d", df['date'].isnull().sum())
            logger.info(f"Missing amounts: {df['amount'].isna().sum()}")
            logger.info(f"Missing countries: {df['country'].isna().sum()}")
            logger.info(f"Missing articles: {df['article'].isna().sum()}")
            
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")

    async def run(self):
        """Run the scraper"""
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            self.page = await context.new_page()

            try:
                # Navigate to initial page
                logging.info("Navigating to the enforcement tracker...")
                await self.page.goto(self.base_url)
                await self.page.wait_for_selector('table.table')
                await self.page.wait_for_load_state('networkidle')
                
                # Scrape the fines
                fines = await self.scrape_fines()
                
                if not fines:
                    logging.error("No fines were scraped!")
                    return
                
                logging.info(f"Successfully scraped {len(fines)} fines")
                
                # Save the data
                self.save_raw_data(fines)
                logging.info("Data saved successfully")
                
            except Exception as e:
                logging.error(f"Error during scraping: {str(e)}")
                raise
            
            finally:
                await browser.close()

    def process_row(self, row):
        cells = row.find_all('td')
        if len(cells) < 13:  # We expect at least 13 cells
            return None
        
        try:
            # Get the date text from cell 4 (0-based index)
            date_text = cells[4].get_text(strip=True)
            if not date_text:
                return None
            
            # Parse the date and convert to ISO format string immediately
            date = datetime.strptime(date_text, '%Y-%m-%d').date().isoformat()
            
            # Extract other fields
            fine = {
                'etid': cells[1].get_text(strip=True),
                'country': cells[2].get_text(strip=True).split('\n')[-1],
                'authority': cells[3].get_text(strip=True),
                'date': date,  # Now this is already a string
                'amount': cells[5].get_text(strip=True),
                'company': cells[6].get_text(strip=True),
                'sector': cells[7].get_text(strip=True),
                'article': cells[8].get_text(strip=True),
                'type': cells[9].get_text(strip=True),
                'summary': cells[10].get_text(strip=True),
                'source': cells[11].find('a')['href'] if cells[11].find('a') else None,
                'url': cells[12].find('a')['href'] if cells[12].find('a') else None
            }
            return fine
        except (ValueError, IndexError, KeyError, AttributeError) as e:
            logging.error(f"Error processing row: {str(e)}")
            return None

    def save_data(self):
        """Save the scraped fines to a JSON file."""
        try:
            # Save raw data
            with open('data/gdpr_fines.json', 'w', encoding='utf-8') as f:
                json.dump(self.fines, f, indent=2, ensure_ascii=False)
            logging.info(f"Successfully saved {len(self.fines)} fines to data/gdpr_fines.json")
        except Exception as e:
            logging.error(f"Error saving data: {str(e)}")
            raise

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create and run scraper
    scraper = GDPRScraper()
    asyncio.run(scraper.run()) 
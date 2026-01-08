"""
Google Ads Transparency Scraper
This script scrapes advertiser information from Google Ads Transparency Center
for search queries A-Z to get all advertisers with their links.
"""

import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import time
from urllib.parse import urlencode
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class GoogleAdsTransparencyScraper:
    def __init__(self):
        self.base_url = "https://adstransparency.google.com/search"
        self.all_advertisers = []
        
    async def scrape_query(self, page, query_letter):
        """Scrape advertisers for a specific query letter"""
        try:
            # Build URL with query parameter
            params = {'region': 'anywhere', 'query': query_letter}
            url = f"{self.base_url}?{urlencode(params)}"
            
            logger.info(f"Scraping query: {query_letter} - URL: {url}")
            
            # Navigate to the page
            await page.goto(url, wait_until='networkidle', timeout=60000)
            
            # Wait for content to load
            await page.wait_for_timeout(3000)
            
            # Scroll to load more results
            await self.scroll_page(page)
            
            # Extract advertiser data
            advertisers = await self.extract_advertisers(page, query_letter)
            
            logger.info(f"Found {len(advertisers)} advertisers for query '{query_letter}'")
            
            return advertisers
            
        except Exception as e:
            logger.error(f"Error scraping query '{query_letter}': {str(e)}")
            return []
    
    async def scroll_page(self, page, max_scrolls=10):
        """Scroll the page to load more results"""
        logger.info("Scrolling page to load more results...")
        
        for i in range(max_scrolls):
            # Scroll to bottom
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(2000)
            
            # Check if "Load more" button exists and click it
            try:
                load_more_button = await page.query_selector('button:has-text("Load more")')
                if load_more_button:
                    await load_more_button.click()
                    await page.wait_for_timeout(2000)
                    logger.info("Clicked 'Load more' button")
            except:
                pass
            
    async def extract_advertisers(self, page, query_letter):
        """Extract advertiser information from the page"""
        advertisers = []
        
        try:
            # Wait for advertiser cards to load
            await page.wait_for_selector('[ng-if*="advertiser"], [class*="advertiser"], a[href*="/advertiser/"]', timeout=10000)
            
            # Get all advertiser links
            advertiser_links = await page.query_selector_all('a[href*="/advertiser/"]')
            
            for link in advertiser_links:
                try:
                    # Get advertiser name
                    name_element = await link.query_selector('[class*="name"], .advertiser-name, h2, h3, span')
                    name = await name_element.inner_text() if name_element else "Unknown"
                    
                    # Get advertiser URL
                    href = await link.get_attribute('href')
                    if href:
                        # Make absolute URL if relative
                        if href.startswith('/'):
                            href = f"https://adstransparency.google.com{href}"
                    
                    # Get additional info if available
                    region_element = await link.query_selector('[class*="region"], .advertiser-region')
                    region = await region_element.inner_text() if region_element else ""
                    
                    advertiser_data = {
                        'query': query_letter,
                        'name': name.strip(),
                        'url': href,
                        'region': region.strip() if region else ""
                    }
                    
                    # Avoid duplicates
                    if advertiser_data not in advertisers:
                        advertisers.append(advertiser_data)
                    
                except Exception as e:
                    logger.debug(f"Error extracting advertiser: {str(e)}")
                    continue
            
            # Alternative: Try to extract from Angular/React data
            if len(advertisers) == 0:
                advertisers = await self.extract_from_js_data(page, query_letter)
                
        except Exception as e:
            logger.error(f"Error extracting advertisers: {str(e)}")
        
        return advertisers
    
    async def extract_from_js_data(self, page, query_letter):
        """Try to extract data from JavaScript variables or DOM"""
        advertisers = []
        
        try:
            # Try to extract data from the page content
            page_content = await page.content()
            
            # Look for specific patterns in the HTML
            # This is a fallback method
            logger.info("Attempting to extract from page source...")
            
            # You can add custom extraction logic here based on the page structure
            
        except Exception as e:
            logger.error(f"Error in fallback extraction: {str(e)}")
        
        return advertisers
    
    async def run(self, queries=None):
        """Main scraping function"""
        if queries is None:
            # Generate A-Z queries
            queries = [chr(i) for i in range(ord('a'), ord('z') + 1)]
        
        logger.info(f"Starting scraper for {len(queries)} queries: {queries}")
        
        async with async_playwright() as playwright:
            # Launch browser
            browser = await playwright.chromium.launch(
                headless=False,  # Set to True for background execution
                args=['--start-maximized']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            
            # Scrape each query
            for query in queries:
                try:
                    advertisers = await self.scrape_query(page, query)
                    self.all_advertisers.extend(advertisers)
                    
                    # Add delay between requests
                    await page.wait_for_timeout(2000)
                    
                except Exception as e:
                    logger.error(f"Error processing query '{query}': {str(e)}")
                    continue
            
            await browser.close()
        
        # Save results
        self.save_results()
        
        logger.info(f"Scraping completed. Total advertisers found: {len(self.all_advertisers)}")
        
    def save_results(self):
        """Save results to CSV and JSON"""
        if not self.all_advertisers:
            logger.warning("No advertisers found to save!")
            return
        
        # Create DataFrame
        df = pd.DataFrame(self.all_advertisers)
        
        # Remove duplicates based on URL
        df = df.drop_duplicates(subset=['url'], keep='first')
        
        # Save to CSV
        csv_filename = f'google_ads_advertisers_{time.strftime("%Y%m%d_%H%M%S")}.csv'
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        logger.info(f"Results saved to {csv_filename}")
        
        # Save to JSON
        json_filename = f'google_ads_advertisers_{time.strftime("%Y%m%d_%H%M%S")}.json'
        df.to_json(json_filename, orient='records', indent=2, force_ascii=False)
        logger.info(f"Results saved to {json_filename}")
        
        # Print summary
        print("\n" + "="*50)
        print(f"SCRAPING SUMMARY")
        print("="*50)
        print(f"Total advertisers found: {len(df)}")
        print(f"Unique queries processed: {df['query'].nunique()}")
        print(f"\nResults saved to:")
        print(f"  - {csv_filename}")
        print(f"  - {json_filename}")
        print("="*50 + "\n")


if __name__ == "__main__":
    scraper = GoogleAdsTransparencyScraper()
    
    # Run the scraper
    # You can customize queries here, e.g., ['a', 'b', 'c'] for testing
    asyncio.run(scraper.run())

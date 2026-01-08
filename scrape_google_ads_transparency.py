"""
Google Ads Transparency Scraper
Extracts advertiser data including advertiser URLs and sample ad URLs
"""

import time
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class GoogleAdsTransparencyScraper:
    def __init__(self, start_query="a", region="anywhere", output_file="advertisers_data.csv"):
        """
        Initialize the scraper
        
        Args:
            start_query: Initial search query (default: "a")
            region: Region code (default: "anywhere")
            output_file: Output CSV filename
        """
        self.base_url = f"https://adstransparency.google.com/search?region={region}&query={start_query}"
        self.region = region
        self.output_file = output_file
        self.data = []
        self.driver = None
        self.scraped_advertisers = set()  # Track scraped advertisers to avoid duplicates
        
    def setup_driver(self):
        """Initialize Selenium WebDriver"""
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Uncomment for headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def extract_advertiser_data(self):
        """Extract advertiser data from current page"""
        try:
            # Wait for listbox to load
            wait = WebDriverWait(self.driver, 15)
            listbox = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='listbox']"))
            )
            
            # Wait a bit for all elements to render
            time.sleep(2)
            
            # Get all options (advertiser items)
            options = self.driver.find_elements(By.CSS_SELECTOR, "[role='option']")
            print(f"Found {len(options)} advertisers on this page")
            
            for idx, option in enumerate(options):
                try:
                    # Extract advertiser name
                    name_elem = option.find_element(By.CSS_SELECTOR, "span:first-child")
                    advertiser_name = name_elem.text.strip()
                    
                    # Skip if already scraped
                    if advertiser_name in self.scraped_advertisers:
                        continue
                    
                    # Extract number of ads
                    ads_text = None
                    based_in = None
                    verified = False
                    
                    # Get all text content
                    text_content = option.text
                    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                    
                    # Parse lines
                    for line in lines:
                        if "ad" in line.lower() and any(char.isdigit() for char in line):
                            ads_text = line.strip()
                        elif "Based in:" in line:
                            based_in = line.replace("Based in:", "").strip()
                    
                    # Check if verified
                    try:
                        option.find_element(By.XPATH, ".//span[contains(text(), 'verified') or contains(text(), 'Verified')]")
                        verified = True
                    except NoSuchElementException:
                        verified = False
                    
                    # Get advertiser URL and one ad link
                    advertiser_url, ad_link = self.get_advertiser_and_ad_url(option, advertiser_name)
                    
                    # Store data
                    data_dict = {
                        "advertiser_name": advertiser_name,
                        "number_of_ads": ads_text,
                        "based_in": based_in,
                        "verified": verified,
                        "advertiser_url": advertiser_url,
                        "sample_ad_url": ad_link,
                        "scrape_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    self.data.append(data_dict)
                    self.scraped_advertisers.add(advertiser_name)
                    print(f"✓ [{idx+1}/{len(options)}] {advertiser_name} | Ads: {ads_text} | Location: {based_in} | Verified: {verified}")
                    
                except Exception as e:
                    print(f"Error extracting advertiser {idx+1}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error in extract_advertiser_data: {str(e)}")
    
    def get_advertiser_and_ad_url(self, option_element, advertiser_name):
        """
        Get the advertiser URL and one ad URL by clicking through
        """
        advertiser_url = None
        ad_link = None
        original_url = self.driver.current_url
        
        try:
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option_element)
            time.sleep(0.5)
            
            # Click the option to navigate to advertiser page
            option_element.click()
            time.sleep(3)
            
            # Get advertiser URL
            current_url = self.driver.current_url
            if "advertiser" in current_url:
                advertiser_url = current_url
                
                # Now try to get one ad link
                try:
                    wait = WebDriverWait(self.driver, 10)
                    # Look for ad creative cards or links
                    ad_elements = self.driver.find_elements(By.CSS_SELECTOR, "[role='option'], a[href*='/creative/']")
                    
                    if ad_elements:
                        for ad_elem in ad_elements[:5]:  # Check first 5 elements
                            try:
                                ad_elem.click()
                                time.sleep(2)
                                
                                if "/creative/" in self.driver.current_url:
                                    ad_link = self.driver.current_url
                                    break
                            except:
                                continue
                                
                except Exception as e:
                    print(f"  Could not extract ad link for {advertiser_name}: {str(e)}")
            
            # Navigate back to search results
            self.driver.get(original_url)
            time.sleep(2)
            
        except Exception as e:
            print(f"  Error getting URLs for {advertiser_name}: {str(e)}")
            # Try to navigate back
            try:
                self.driver.get(original_url)
                time.sleep(2)
            except:
                pass
        
        return advertiser_url, ad_link
    
    def check_next_button(self):
        """Check if Next button is enabled"""
        try:
            next_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Next')]")
            is_disabled = next_button.get_attribute("aria-disabled") == "true"
            is_enabled = not is_disabled and next_button.is_enabled()
            return is_enabled, next_button
        except:
            return False, None
    
    def click_next_page(self, next_button):
        """Click the Next button to go to next page"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(0.5)
            next_button.click()
            time.sleep(3)  # Wait for page to load
            return True
        except Exception as e:
            print(f"Error clicking next button: {str(e)}")
            return False
    
    def scrape_all_pages(self, max_pages=None):
        """
        Scrape all pages of results
        
        Args:
            max_pages: Maximum number of pages to scrape (None for all pages)
        """
        page_count = 1
        
        try:
            self.setup_driver()
            print(f"Opening: {self.base_url}")
            self.driver.get(self.base_url)
            time.sleep(4)  # Initial page load
            
            while True:
                print(f"\n{'='*80}")
                print(f"📄 Processing Page {page_count}...")
                print(f"{'='*80}")
                
                # Extract data from current page
                self.extract_advertiser_data()
                
                # Check if we've reached max pages
                if max_pages and page_count >= max_pages:
                    print(f"\n✓ Reached maximum pages limit ({max_pages})")
                    break
                
                # Check if Next button is available and enabled
                is_enabled, next_button = self.check_next_button()
                
                if is_enabled:
                    print(f"\n➜ Moving to page {page_count + 1}...")
                    if self.click_next_page(next_button):
                        page_count += 1
                    else:
                        print("Could not click next button, stopping...")
                        break
                else:
                    print("\n✓ Reached end of results (Next button disabled or not found)")
                    break
                    
        except KeyboardInterrupt:
            print("\n\n⚠ Scraping interrupted by user")
        except Exception as e:
            print(f"\n❌ Error during scraping: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
                print("\n✓ Browser closed")
    
    def save_to_csv(self):
        """Save collected data to CSV file"""
        if not self.data:
            print("No data to save")
            return
        
        try:
            fieldnames = ["advertiser_name", "number_of_ads", "based_in", "verified", 
                         "advertiser_url", "sample_ad_url", "scrape_date"]
            
            with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.data)
            
            print(f"\n✓ Data saved to {self.output_file}")
            print(f"Total advertisers scraped: {len(self.data)}")
            
        except Exception as e:
            print(f"Error saving to CSV: {str(e)}")
    
    def print_summary(self):
        """Print summary of scraped data"""
        if not self.data:
            print("No data scraped")
            return
        
        print(f"\n{'='*80}")
        print(f"SCRAPING SUMMARY")
        print(f"{'='*80}")
        print(f"Total Advertisers: {len(self.data)}")
        verified_count = sum(1 for d in self.data if d['verified'])
        print(f"Verified: {verified_count}")
        print(f"Unverified: {len(self.data) - verified_count}")
        
        with_ad_links = sum(1 for d in self.data if d['sample_ad_url'])
        print(f"With Ad Links: {with_ad_links}")
        print(f"{'='*80}")
        
        # Print first 5 records as sample
        print("\nSample Data (First 5):")
        for i, record in enumerate(self.data[:5], 1):
            print(f"\n{i}. {record['advertiser_name']}")
            print(f"   Ads: {record['number_of_ads']}")
            print(f"   Based in: {record['based_in']}")
            print(f"   Verified: {record['verified']}")
            print(f"   Advertiser URL: {record['advertiser_url']}")
            print(f"   Sample Ad URL: {record['sample_ad_url']}")

# Usage Example
if __name__ == "__main__":
    # Initialize scraper
    scraper = GoogleAdsTransparencyScraper(
        start_query="a",
        region="anywhere",
        output_file="google_ads_transparency.csv"
    )
    
    # Run scraper (set max_pages to limit, or None for all pages)
    print("Starting Google Ads Transparency Scraper...")
    print("⚠ Note: This will take time as it visits each advertiser page\n")
    
    scraper.scrape_all_pages(max_pages=5)  # Change to None to scrape all pages
    
    # Save results
    scraper.save_to_csv()
    
    # Print summary
    scraper.print_summary()

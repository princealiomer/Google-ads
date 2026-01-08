"""
Google Ads Transparency Advanced Scraper with Selenium
Extracts advertiser data and all creative URLs from each advertiser page
"""

import time
import csv
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class GoogleAdsTransparencyScraperAdvanced:
    def __init__(self, start_query="a", region="US", output_csv="advertisers_data.csv", output_json="creative_urls.json"):
        """
        Initialize the advanced scraper
        
        Args:
            start_query: Initial search query (default: "a")
            region: Region code (default: "US")
            output_csv: Output CSV filename for advertiser summary
            output_json: Output JSON filename for all URLs
        """
        self.base_url = f"https://adstransparency.google.com/search?region={region}&query={start_query}"
        self.region = region
        self.output_csv = output_csv
        self.output_json = output_json
        self.advertisers_data = []
        self.all_urls = []
        self.driver = None
        
    def setup_driver(self):
        """Initialize Selenium WebDriver"""
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Uncomment for headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
    def extract_advertiser_data_from_search_page(self):
        """Extract advertiser data from search results page"""
        try:
            wait = WebDriverWait(self.driver, 10)
            listbox = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='listbox']"))
            )
            
            options = self.driver.find_elements(By.CSS_SELECTOR, "[role='option']")
            
            for option in options:
                try:
                    text_content = option.text
                    lines = text_content.split('\n')
                    
                    advertiser_name = lines[0] if len(lines) > 0 else ""
                    ads_text = None
                    based_in = None
                    verified = False
                    
                    for line in lines:
                        if "ads" in line:
                            ads_text = line.strip()
                        elif "Based in:" in line:
                            based_in = line.replace("Based in:", "").strip()
                    
                    verified_elem = option.find_elements(By.XPATH, ".//span[contains(text(), 'verified')]")
                    verified = len(verified_elem) > 0
                    
                    data_dict = {
                        "advertiser_name": advertiser_name,
                        "number_of_ads": ads_text,
                        "based_in": based_in,
                        "verified": verified,
                        "advertiser_page_url": None,
                        "creative_urls": [],
                        "scrape_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    self.advertisers_data.append(data_dict)
                    print(f"✓ Found: {advertiser_name} - {ads_text} - {based_in}")
                    
                except Exception as e:
                    print(f"Error extracting advertiser data: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error in extract_advertiser_data_from_search_page: {str(e)}")
    
    def extract_creative_urls_from_advertiser_page(self, advertiser_index):
        """
        Extract all creative URLs from an advertiser's page
        
        Args:
            advertiser_index: Index of the advertiser in the list
        """
        try:
            # Get advertiser page URL
            advertiser_page_url = self.driver.current_url
            self.advertisers_data[advertiser_index]["advertiser_page_url"] = advertiser_page_url
            
            print(f"\n📄 Extracting creatives from: {advertiser_page_url}")
            
            # Find all creative links
            creative_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/creative/')]")
            
            creative_urls = []
            for link in creative_links:
                href = link.get_attribute("href")
                if href and "/creative/" in href:
                    # Construct full URL
                    if href.startswith("http"):
                        full_url = href
                    else:
                        full_url = "https://adstransparency.google.com" + href
                    
                    creative_urls.append(full_url)
                    self.all_urls.append({
                        "advertiser_name": self.advertisers_data[advertiser_index]["advertiser_name"],
                        "advertiser_page_url": advertiser_page_url,
                        "creative_url": full_url,
                        "scrape_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            
            # Remove duplicates
            self.advertisers_data[advertiser_index]["creative_urls"] = list(set(creative_urls))
            
            print(f"✓ Found {len(set(creative_urls))} unique creative URLs")
            
        except Exception as e:
            print(f"Error extracting creative URLs: {str(e)}")
    
    def navigate_to_advertiser(self, advertiser_index):
        """Navigate to an advertiser's page and extract data"""
        try:
            # Wait for listbox and get the option
            wait = WebDriverWait(self.driver, 10)
            listbox = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='listbox']"))
            )
            
            options = self.driver.find_elements(By.CSS_SELECTOR, "[role='option']")
            
            if advertiser_index < len(options):
                option = options[advertiser_index]
                option.click()
                time.sleep(3)  # Wait for page to load
                
                # Extract creative URLs from advertiser page
                self.extract_creative_urls_from_advertiser_page(advertiser_index)
                
                # Go back to search results
                self.driver.back()
                time.sleep(2)
                
        except Exception as e:
            print(f"Error navigating to advertiser: {str(e)}")
    
    def check_next_button(self):
        """Check if Next button is enabled"""
        try:
            next_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Next')]")
            is_enabled = next_button.get_attribute("aria-disabled") != "true"
            return is_enabled, next_button
        except:
            return False, None
    
    def click_next_page(self, next_button):
        """Click the Next button to go to next page"""
        try:
            next_button.click()
            time.sleep(2)
            return True
        except Exception as e:
            print(f"Error clicking next button: {str(e)}")
            return False
    
    def scrape_all_pages(self, visit_advertiser_pages=True):
        """
        Scrape all pages of results
        
        Args:
            visit_advertiser_pages: If True, visit each advertiser page to extract creative URLs
        """
        page_count = 1
        advertiser_count = 0
        
        try:
            self.setup_driver()
            self.driver.get(self.base_url)
            time.sleep(3)
            
            while True:
                print(f"\n{'='*80}")
                print(f"📄 Processing Page {page_count}...")
                print(f"{'='*80}")
                
                # Extract data from current page
                self.extract_advertiser_data_from_search_page()
                
                # If requested, visit each advertiser page on this page to get creative URLs
                if visit_advertiser_pages:
                    options = self.driver.find_elements(By.CSS_SELECTOR, "[role='option']")
                    num_on_page = len(options)
                    
                    for i in range(num_on_page):
                        advertiser_count += 1
                        print(f"\n[{advertiser_count}] Visiting advertiser page...")
                        self.navigate_to_advertiser(i)
                
                # Check if Next button is available and enabled
                is_enabled, next_button = self.check_next_button()
                
                if is_enabled:
                    print(f"\n➜ Moving to next page...")
                    if self.click_next_page(next_button):
                        page_count += 1
                    else:
                        break
                else:
                    print(f"\n✓ Reached end of results (Next button disabled)")
                    break
                    
        except Exception as e:
            print(f"Error during scraping: {str(e)}")
        finally:
            self.driver.quit()
    
    def save_to_csv(self):
        """Save advertiser summary to CSV file"""
        if not self.advertisers_data:
            print("No data to save")
            return
        
        try:
            fieldnames = [
                "advertiser_name",
                "number_of_ads",
                "based_in",
                "verified",
                "advertiser_page_url",
                "creative_count",
                "scrape_date"
            ]
            
            with open(self.output_csv, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for data in self.advertisers_data:
                    writer.writerow({
                        "advertiser_name": data["advertiser_name"],
                        "number_of_ads": data["number_of_ads"],
                        "based_in": data["based_in"],
                        "verified": data["verified"],
                        "advertiser_page_url": data["advertiser_page_url"],
                        "creative_count": len(data["creative_urls"]),
                        "scrape_date": data["scrape_date"]
                    })
            
            print(f"\n✓ Advertiser summary saved to {self.output_csv}")
            
        except Exception as e:
            print(f"Error saving to CSV: {str(e)}")
    
    def save_urls_to_json(self):
        """Save all URLs (advertiser and creative) to JSON file"""
        if not self.all_urls:
            print("No URLs to save")
            return
        
        try:
            with open(self.output_json, 'w', encoding='utf-8') as jsonfile:
                json.dump(self.all_urls, jsonfile, indent=2, ensure_ascii=False)
            
            print(f"✓ All URLs saved to {self.output_json}")
            
        except Exception as e:
            print(f"Error saving to JSON: {str(e)}")
    
    def save_all_creative_urls_by_advertiser(self, output_file="creative_urls_by_advertiser.json"):
        """Save creative URLs organized by advertiser"""
        try:
            organized_data = []
            
            for advertiser in self.advertisers_data:
                organized_data.append({
                    "advertiser_name": advertiser["advertiser_name"],
                    "number_of_ads": advertiser["number_of_ads"],
                    "based_in": advertiser["based_in"],
                    "verified": advertiser["verified"],
                    "advertiser_page_url": advertiser["advertiser_page_url"],
                    "creative_urls": advertiser["creative_urls"],
                    "total_creatives_found": len(advertiser["creative_urls"])
                })
            
            with open(output_file, 'w', encoding='utf-8') as jsonfile:
                json.dump(organized_data, jsonfile, indent=2, ensure_ascii=False)
            
            print(f"✓ Creative URLs by advertiser saved to {output_file}")
            
        except Exception as e:
            print(f"Error saving creative URLs by advertiser: {str(e)}")
    
    def print_summary(self):
        """Print summary of scraped data"""
        if not self.advertisers_data:
            print("No data scraped")
            return
        
        print(f"\n{'='*80}")
        print(f"SCRAPING SUMMARY")
        print(f"{'='*80}")
        print(f"Total Advertisers: {len(self.advertisers_data)}")
        verified_count = sum(1 for d in self.advertisers_data if d['verified'])
        print(f"Verified: {verified_count}")
        print(f"Unverified: {len(self.advertisers_data) - verified_count}")
        print(f"Total Creative URLs Extracted: {len(self.all_urls)}")
        print(f"{'='*80}")
        
        # Print first 3 records as sample
        print("\nSample Data (First 3 Advertisers):")
        for i, record in enumerate(self.advertisers_data[:3], 1):
            print(f"\n{i}. {record['advertiser_name']}")
            print(f"   Ads: {record['number_of_ads']}")
            print(f"   Based in: {record['based_in']}")
            print(f"   Verified: {record['verified']}")
            print(f"   Advertiser Page: {record['advertiser_page_url']}")
            print(f"   Creatives Found: {len(record['creative_urls'])}")
            if record['creative_urls']:
                print(f"   Sample Creative URLs:")
                for url in record['creative_urls'][:2]:
                    print(f"     - {url}")

# Usage Example
if __name__ == "__main__":
    # Initialize scraper
    scraper = GoogleAdsTransparencyScraperAdvanced(
        start_query="a",
        region="US",
        output_csv="google_ads_advertisers.csv",
        output_json="google_ads_all_urls.json"
    )
    
    # Run scraper (with advertiser page visits)
    print("Starting Google Ads Transparency Advanced Scraper...")
    print("This will extract advertiser URLs and all creative URLs from each advertiser page")
    scraper.scrape_all_pages(visit_advertiser_pages=True)
    
    # Save results
    scraper.save_to_csv()
    scraper.save_urls_to_json()
    scraper.save_all_creative_urls_by_advertiser("creative_urls_detailed.json")
    
    # Print summary
    scraper.print_summary()

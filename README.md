# Google Ads Transparency Scraper

This project contains multiple scrapers for Google's Ads Transparency Center:

- **Playwright Scraper** (`scrape_google_ads_transparency.py`) - Basic scraper for advertiser data
- **Selenium Advanced Scraper** (`scrape_advanced_selenium.py`) - Extracts creative URLs from each advertiser page
- **Streamlit Web App** (`app.py`) - Interactive dashboard for viewing and analyzing scraped data

## Features

- Scrapes all advertisers for queries A through Z
- Handles dynamic JavaScript content
- Extracts advertiser names, URLs, and regions
- Exports data to CSV and JSON formats
- Automatic scrolling and "Load More" button handling
- Duplicate removal
- Comprehensive logging

## Installation

1. Install Python 3.8 or higher

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:

```bash
playwright install chromium
```

## Usage

### Option 1: Playwright Scraper (Basic)

Scrapes advertiser data from search results:

```bash
pip install -r requirements-scraper.txt
playwright install chromium
python scrape_google_ads_transparency.py
```

### Option 2: Selenium Advanced Scraper (With Creative URLs)

Visits each advertiser page and extracts all creative URLs:

```bash
pip install -r requirements-selenium.txt
# Make sure Chrome/ChromeDriver is installed
python scrape_advanced_selenium.py
```

**Features:**

- Navigates through all search result pages
- Visits each advertiser's page
- Extracts all creative URLs
- Saves data in multiple formats (CSV, JSON)

### Option 3: Streamlit Web App (View Data)

Interactive dashboard for analyzing scraped data:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Output

The scraper generates two files:

- `google_ads_advertisers_YYYYMMDD_HHMMSS.csv` - CSV format
- `google_ads_advertisers_YYYYMMDD_HHMMSS.json` - JSON format

### CSV Columns:

- `query` - The search query letter used
- `name` - Advertiser name
- `url` - Link to advertiser's transparency page
- `region` - Advertiser's region (if available)

## Configuration

You can modify the following settings in `scrape_google_ads_transparency.py`:

- `headless=False` → Set to `True` to run browser in background
- `max_scrolls=10` → Increase to load more results per query
- Delays between requests (default: 2000ms)

## Troubleshooting

### Issue: No advertisers found

- Check your internet connection
- The page structure might have changed - inspect the HTML
- Try running with `headless=False` to see what's happening

### Issue: Browser not launching

```bash
playwright install chromium --force
```

### Issue: Import errors

```bash
pip install -r requirements.txt --upgrade
```

## Logs

Check `scraper.log` for detailed execution logs.

## Notes

- The script respects rate limiting with delays between requests
- Duplicates are automatically removed based on advertiser URL
- The scraper handles pagination by scrolling and clicking "Load More" buttons

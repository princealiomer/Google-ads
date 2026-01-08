# Google Ads Transparency Scraper

This tool scrapes advertiser information from Google's Ads Transparency Center for queries A-Z.

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

### Basic Usage (Scrape A-Z):

```bash
python scrape_google_ads_transparency.py
```

### Customize Queries:

Edit the `scrape_google_ads_transparency.py` file and modify the `run()` call at the bottom:

```python
# Example: Only scrape specific letters
asyncio.run(scraper.run(queries=['a', 'b', 'c']))
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

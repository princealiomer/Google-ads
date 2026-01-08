# Google Ads Transparency Scraper

A Selenium-based scraper for extracting advertiser data and creative URLs from Google Ads Transparency Center.

## 🚀 Features

- Extracts advertiser information (name, location, verification status, ad count)
- Visits each advertiser page to collect all creative URLs
- Navigates through all search result pages automatically
- Saves data in multiple formats (CSV, JSON)
- Interactive Streamlit dashboard for data visualization

## 📋 Requirements

- Python 3.9+
- Chrome browser
- ChromeDriver (automatically managed by Selenium)

## 🛠️ Installation

### For Scraping (Local Only)

```bash
pip install -r requirements-scraper.txt
```

### For Streamlit Dashboard

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📊 Usage

### Run the Scraper

```bash
python scrape_google_ads_transparency.py
```

This will:

1. Navigate to Google Ads Transparency Center
2. Extract advertiser data from search results
3. Visit each advertiser's page
4. Collect all creative URLs
5. Save results to CSV and JSON files

### View Results in Dashboard

```bash
streamlit run app.py
```

Then upload your scraped CSV files or use the sample data.

## 📁 Output Files

The scraper generates:

- `google_ads_advertisers.csv` - Summary of advertisers
- `google_ads_all_urls.json` - All creative URLs
- `creative_urls_detailed.json` - Creative URLs organized by advertiser

## ⚙️ Configuration

Edit the scraper initialization in `scrape_google_ads_transparency.py`:

```python
scraper = GoogleAdsTransparencyScraperAdvanced(
    start_query="a",      # Search query
    region="US",          # Region code
    output_csv="...",     # CSV output filename
    output_json="..."     # JSON output filename
)
```

## 🌐 Streamlit Cloud Deployment

The Streamlit app (`app.py`) can be deployed to Streamlit Cloud for viewing and analyzing scraped data.

**Note:** The scraper itself cannot run on Streamlit Cloud (requires browser automation). Run it locally and upload the results to the dashboard.

## 📝 License

MIT License

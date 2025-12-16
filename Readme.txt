IMDb User Review Scraper - Running Guide

Overview
This Python script scrapes IMDb movie user reviews and saves review titles, content, and ratings in CSV files. Any reviews marked as spoilers are automatically expanded to ensure the full text is retrieved.

Environment Requirements
- Python 3.8+
- Chrome Browser (latest version)
- ChromeDriver (matching your Chrome version)

Install Dependencies
1. Navigate to the project directory:
   cd IMDB_Scraper

2. Install Python packages:
   pip install -r requirements.txt

   If requirements.txt is not available, install manually:
   pip install pandas selenium gensim nltk regex python-dateutil textblob

ChromeDriver Setup
1. Check your Chrome version (Menu → Help → About Google Chrome).
2. Download the matching ChromeDriver from:
   https://chromedriver.chromium.org/
3. Extract and place it in the project directory:
   IMDB_Scraper/ChromeDrive/chromedriver/chromedriver
4. macOS/Linux: set execution permission:
   chmod +x IMDB_Scraper/ChromeDrive/chromedriver/chromedriver
5. Update the ChromeDriver path in scraper.py:
   PATH = "IMDB_Scraper/ChromeDrive/chromedriver/chromedriver"

Run the Script
    python scraper.py


Output Files
- reviews.csv: Review data (Review_Index, Review_Title, Review_Content, Has_Spoiler, Rating, movie_id)
- stats.csv: Summary statistics (Total reviews, reviews with title/content, reviews with spoilers, Movie ID, URL, page title)

Notes
- ChromeDriver version must match your Chrome version to avoid errors.
- Ensure PATH points to the correct ChromeDriver location.
- If the "See All" button fails to load all reviews, refresh manually.
- Script includes delays to prevent being blocked.
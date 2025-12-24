# Zootopia IMDb Review Analysis – personal notes

## What is this?
This project performs textual analysis on IMDb user reviews for *Zootopia*.

It consists of three research questions:
- **RQ1 & RQ2**: LDA topic modelling + topic concentration analysis
- **RQ3**: unigram / bigram / trigram frequency comparison
- **Data collection**: IMDb user review scraping using Selenium

This README is for **personal organisation and reproducibility**, not for formal submission.

---

## Project Structure (logical)

- `_scraper/` – IMDb review scraper and ChromeDriver
- `_data/raw/` – raw scraped review data
- `_data/rq1_rq2/` – cleaned data and outputs for RQ1 & RQ2
- `_data/rq3/` – cleaned data and n-gram results for RQ3

Core scripts:
- `rq1_rq2_clean.py` – data cleaning for RQ1 & RQ2
- `rq1_rq2_lda.py` – LDA modelling and concentration analysis
- `rq3_clean.py` – data cleaning for RQ3
- `rq3_ngram_analysis.py` – unigram / bigram / trigram analysis

---

## How to rerun the analysis

### RQ1 & RQ2 (Topic Modelling)

```bash
python rq1_rq2_clean.py
python rq1_rq2_lda.py
```

### RQ3 (n-gram Analysis)

```bash
python rq3_clean.py
python rq3_ngram_analysis.py

```

---

## Data

- Raw scraped data: `_data/raw`
- RQ1 & RQ2 outputs: `_data/rq1_rq2`
- RQ3 outputs: `_data/rq3`

**Note:**  
All contents in the `_data/` folder are **generated results after running the scripts**.  
They are provided for convenience and **do not need to be downloaded separately**.  
If required, all results can be reproduced by rerunning the corresponding scripts.

---

# IMDb User Review Scraper – Running Guide

## Overview

This Python script scrapes IMDb movie user reviews and saves review titles, content, and ratings into CSV files.

Key features:

- Reviews marked as **spoilers are automatically expanded**
- Output is structured and ready for downstream NLP analysis

---

## Environment Requirements

- Python 3.8+
- Google Chrome (latest version)
- ChromeDriver (must match Chrome version)

---

## Install Dependencies

1. Navigate to the scraper directory:

```bash
cd IMDB_Scraper

```

1. Install required packages:

```bash
pip install -r requirements.txt

```

If `requirements.txt` is not available, install manually:

```bash
pip install pandas selenium gensim nltk regex python-dateutil textblob

```

---

## ChromeDriver Setup

1. Check your Chrome version
    
    *(Chrome menu → Help → About Google Chrome)*
    
2. Download the matching ChromeDriver from:
    
    https://chromedriver.chromium.org/
    
3. Extract and place it at:

```
IMDB_Scraper/ChromeDrive/chromedriver/chromedriver

```

1. macOS / Linux: set execution permission

```bash
chmod +x IMDB_Scraper/ChromeDrive/chromedriver/chromedriver

```

1. Update the ChromeDriver path in `scraper.py`:

```python
PATH = "IMDB_Scraper/ChromeDrive/chromedriver/chromedriver"

```

---

## Run the Scraper

```bash
python scraper.py

```

---

## Output Files

- `reviews.csv`
    
    Fields:
    
    - Review_Index
    - Review_Title
    - Review_Content
    - Has_Spoiler
    - Rating
    - movie_id
- `stats.csv`
    
    Summary statistics:
    
    - total reviews
    - reviews with title/content
    - reviews with spoilers
    - movie ID
    - URL
    - page title

---

## Notes (Scraper)

- ChromeDriver version **must match** the installed Chrome version.
- Ensure `PATH` points to the correct ChromeDriver location.
- If the "See All" button fails to load all reviews, refresh the page manually.
- Built-in delays are included to reduce the risk of being blocked by IMDb.
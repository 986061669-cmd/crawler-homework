# Douban Top250 Spider

> A modular, polite web spider for scraping the [Douban Movie Top250](https://movie.douban.com/top250) list.
> Built with Python, featuring anti-crawl strategies, structured parsing, and CSV export.

---

## Project Structure

`
CrawlerProject/
  spider.py            # Main spider controller (requests, retries, delays)
  parser.py            # HTML parser (BeautifulSoup, structured extraction)
  storage.py           # Data storage (CSV export via pandas)
  requirements.txt     # Python dependencies
  .gitignore           # Git ignore rules
  README.md            # This file
  data/                # Output directory (auto-created)
    douban_top250_*.csv
`

## Quick Start

### 1. Install Dependencies

`ash
pip install -r requirements.txt
`

### 2. Run the Spider

`ash
python spider.py
`

The spider will:
1. Crawl all 10 pages of Douban Top250 (250 movies)
2. Parse each page for movie details (title, rating, quote, etc.)
3. Save results to data/douban_top250_<timestamp>.csv

### 3. Check Results

Open the generated CSV file in the data/ directory.

---

## Module Overview

| Module | Responsibility |
|---|---|
| spider.py | HTTP requests, header rotation, retry logic, rate limiting |
| parser.py | HTML parsing with BeautifulSoup, structured data extraction |
| storage.py | CSV file output, data formatting, append support |

## Anti-Crawl Strategies

| Strategy | Implementation |
|---|---|
| **User-Agent Rotation** | Random UA from built-in pool or ake-useragent library |
| **Random Delays** | 1-3 second pause between page requests |
| **Retry on Failure** | Up to 3 retries with exponential backoff |
| **Referer Spoofing** | Sets Referer header to Douban homepage |
| **Connection Keep-Alive** | Reuses 
equests.Session for efficiency |
| **Request Timeout** | 15-second timeout to avoid hanging |

## Output Format

Each row in the CSV contains:

| Column | Description |
|---|---|
| Rank | Movie ranking (1-250) |
| Title | Chinese title |
| Title (Other) | English/original title |
| Info | Director, actors, year, country, genre |
| Rating | Average rating (e.g. 9.7) |
| Rating Count | Number of user ratings |
| Quote | Memorable quote |
| Detail URL | Link to movie detail page |

## License

MIT - For educational purposes only. Please respect Douban\'s terms of service.

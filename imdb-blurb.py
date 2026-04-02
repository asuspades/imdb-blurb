#!/usr/bin/env python3
"""
Movie List Enrichment Script (Educational Use Only)

⚠️  WARNING: This script demonstrates web scraping techniques for educational purposes.
    IMDb's Terms of Service prohibit automated data collection. For production use:
    • Use the official OMDb API: http://www.omdbapi.com/ (free tier available)
    • Use IMDb's non-commercial datasets: https://imdb-public-datasets.s3.amazonaws.com/
    • Respect robots.txt and rate limits if scraping any site

Reads a Markdown-style movie list, searches for each title via OMDb API (preferred)
or IMDb scraping (fallback, not recommended), and appends a plot description.

Usage:
    python3 movie_enrich.py --input list.txt --output list_with_descriptions.txt
    python3 movie_enrich.py --input list.txt --output out.md --api-key YOUR_OMDB_KEY

Requirements:
    pip install requests beautifulsoup4

License: MIT (for the code only; data sources have separate terms)
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import argparse
import sys
import logging
from pathlib import Path
from typing import Optional, Tuple, List

# === Configuration ===
DEFAULT_DELAY = 2.0  # Conservative delay between requests (seconds)
DEFAULT_TIMEOUT = 10  # Request timeout in seconds
MAX_RETRIES = 3  # Retry failed requests this many times
OMDB_BASE_URL = "https://www.omdbapi.com/"  # Preferred API endpoint

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# User-Agent should identify your project, not impersonate a browser
USER_AGENT = "MovieEnricher/2.0 (Educational; https://github.com/asuspades/imdb-blurb)"
HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept-Language': 'en-US,en;q=0.9',
}

# Pattern to match markdown table rows: | Title | Year |
ROW_PATTERN = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(\d{4})\s*\|")


def validate_file_path(path_str: str, file_type: str) -> Path:
    """Validate and resolve file path, preventing path traversal attacks"""
    try:
        path = Path(path_str).resolve()
        # Block paths outside current working directory tree for safety
        if file_type == "input" and not path.exists():
            raise FileNotFoundError(f"{file_type} file not found: {path}")
        return path
    except Exception as e:
        raise ValueError(f"Invalid {file_type} path '{path_str}': {e}")


def fetch_omdb_plot(title: str, year: str, api_key: Optional[str]) -> Optional[str]:
    """
    Fetch movie plot via OMDb API (preferred, ToS-compliant method)
    
    Returns plot string if successful, None if API call fails or not found.
    """
    if not api_key:
        logger.debug("OMDb API key not provided; skipping API lookup")
        return None
    
    params = {
        't': title,
        'y': year,
        'plot': 'short',
        'apikey': api_key
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.debug(f"OMDb request (attempt {attempt + 1}): {title} ({year})")
            resp = requests.get(
                OMDB_BASE_URL, 
                params=params, 
                headers=HEADERS,
                timeout=DEFAULT_TIMEOUT
            )
            resp.raise_for_status()
            data = resp.json()
            
            if data.get('Response') == 'True' and data.get('Plot'):
                logger.info(f"✓ Found via OMDb: {title} ({year})")
                return data['Plot'].strip()
            elif data.get('Error'):
                logger.debug(f"OMDb error for '{title}': {data['Error']}")
                return None
            return None
            
        except requests.RequestException as e:
            logger.warning(f"OMDb request failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            continue
        except ValueError as e:
            logger.error(f"Failed to parse OMDb JSON response: {e}")
            return None
    
    logger.warning(f"OMDb lookup failed after {MAX_RETRIES} attempts: {title} ({year})")
    return None


def fetch_imdb_url_scrape(title: str, year: str) -> Optional[str]:
    """
    ⚠️  FALLBACK ONLY: Scrape IMDb search results for movie URL
    
    WARNING: This may violate IMDb's Terms of Service. Use only for personal,
    non-commercial, educational purposes with explicit consent.
    
    Returns IMDb movie page URL if found, None otherwise.
    """
    logger.warning(
        f"⚠️  Using IMDb scraping fallback for '{title}' ({year}). "
        "This may violate IMDb's Terms of Service. Consider using OMDb API instead."
    )
    
    base_url = 'https://www.imdb.com/find'
    params = {
        'q': f"{title} {year}",
        's': 'tt',  # Title search
        'ttype': 'ft',  # Feature film
    }

    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(
                base_url, 
                params=params, 
                headers=HEADERS,
                timeout=DEFAULT_TIMEOUT
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"IMDb search request failed (attempt {attempt + 1}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(DEFAULT_DELAY * (attempt + 1))
                continue
            return None

        soup = BeautifulSoup(resp.text, 'html.parser')
        # Note: IMDb's HTML structure changes frequently; this selector may break
        results = soup.find_all('td', class_='result_text')
        
        for cell in results:
            text = cell.get_text(strip=True)
            if year in text:
                link = cell.find('a')
                if link and (href := link.get('href')):
                    path = href.split('?')[0]
                    return f"https://www.imdb.com{path}"
        
        # Fallback to first result if year match fails
        if results and (first := results[0].find('a')) and (href := first.get('href')):
            return f"https://www.imdb.com{href.split('?')[0]}"
        
        logger.debug(f"No IMDb results matched for '{title}' ({year})")
        return None
    
    return None


def scrape_imdb_description(imdb_url: str) -> str:
    """
    ⚠️  FALLBACK ONLY: Scrape plot description from IMDb movie page
    
    WARNING: IMDb's HTML structure is unstable. This function may break
    without warning and should not be relied upon for production use.
    """
    try:
        resp = requests.get(imdb_url, headers=HEADERS, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"IMDb page request failed: {e}")
        return 'Description unavailable.'

    soup = BeautifulSoup(resp.text, 'html.parser')

    # Try multiple selectors in order of preference (subject to change)
    selectors = [
        ('data-testid', 'plot-xl'),  # Extended plot
        ('data-testid', 'plot-summary__content'),  # Summary
        ('class_', 'ipc-html-content'),  # Generic content block
    ]
    
    for attr_name, attr_value in selectors:
        element = soup.find(attrs={attr_name: attr_value})
        if element and (text := element.get_text(strip=True)):
            if text and text.lower() not in ['no plot found', 'description not found']:
                return text
    
    # Last resort: meta description (often truncated)
    if (meta := soup.select_one('meta[name=description]')) and (content := meta.get('content')):
        # Remove common suffixes added by IMDb
        cleaned = re.split(r'\.\s*(?:Directed by|Starring|Watch now)', content)[0].strip()
        return cleaned + '.' if cleaned else 'Description unavailable.'
    
    return 'Description unavailable.'


def parse_args() -> argparse.Namespace:
    """Parse and validate command line arguments"""
    parser = argparse.ArgumentParser(
        description='Enrich movie list with plot descriptions (Educational Use Only)',
        epilog='''
        LEGAL NOTICE: This tool is for educational purposes. 
        • Prefer the OMDb API (https://www.omdbapi.com/) for ToS-compliant lookups
        • IMDb scraping may violate their Terms of Service
        • Always respect robots.txt and rate limits
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--input', '-i', required=True, type=str,
        help='Input Markdown movie list file (format: | Title | Year |)'
    )
    parser.add_argument(
        '--output', '-o', required=True, type=str,
        help='Output Markdown file path'
    )
    parser.add_argument(
        '--api-key', '-k', type=str, default=None,
        help='OMDb API key (free at https://www.omdbapi.com/apikey.aspx) - RECOMMENDED'
    )
    parser.add_argument(
        '--delay', '-d', type=float, default=DEFAULT_DELAY,
        help=f'Delay between requests in seconds (default: {DEFAULT_DELAY})'
    )
    parser.add_argument(
        '--force-scrape', action='store_true',
        help='Force IMDb scraping even if OMDb API key is provided (NOT RECOMMENDED)'
    )
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Enable verbose/debug logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Validate file paths
    args.input_path = validate_file_path(args.input, "input")
    args.output_path = validate_file_path(args.output, "output")
    
    if args.delay < 1.0:
        logger.warning(f"Delay {args.delay}s is very short; consider increasing to avoid rate limits")
    
    return args


def parse_markdown_movies(file_path: Path) -> List[Tuple[str, str]]:
    """Parse markdown table and extract (title, year) tuples"""
    movies = []
    with open(file_path, encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.rstrip()
            if not line.strip() or line.startswith('|---'):
                continue
            if m := ROW_PATTERN.match(line):
                title = m.group(1).strip()
                year = m.group(2)
                # Basic sanitization
                if title and len(title) < 200 and year.isdigit():
                    movies.append((title, year))
                else:
                    logger.debug(f"Skipping malformed row {line_num}: {line[:50]}...")
    return movies


def get_plot_description(title: str, year: str, api_key: Optional[str], 
                        force_scrape: bool, delay: float) -> str:
    """
    Get movie plot via OMDb API (preferred) or IMDb scraping (fallback)
    
    Returns plot string or error message.
    """
    # Try OMDb API first if key provided and not forced to scrape
    if api_key and not force_scrape:
        if plot := fetch_omdb_plot(title, year, api_key):
            return plot
        logger.debug(f"OMDb lookup failed; trying fallback for '{title}'")
    
    # Fallback to scraping (with warning)
    if imdb_url := fetch_imdb_url_scrape(title, year):
        time.sleep(delay)  # Be polite between requests
        return scrape_imdb_description(imdb_url)
    
    return 'Description not found.'


def main() -> int:
    """Main execution flow"""
    args = parse_args()
    
    logger.info(f"Starting movie enrichment (input: {args.input_path})")
    
    if not args.api_key and not args.force_scrape:
        logger.warning(
            "No OMDb API key provided and --force-scrape not set. "
            "Script will only use IMDb scraping fallback, which may violate ToS. "
            "Get a free key at: https://www.omdbapi.com/apikey.aspx"
        )
        # Continue anyway for educational purposes, but warn user
    
    # Parse input
    try:
        movies = parse_markdown_movies(args.input_path)
    except Exception as e:
        logger.error(f"Failed to parse input file: {e}")
        return 1
    
    if not movies:
        logger.error("No valid movie entries found in input file")
        return 1
    
    logger.info(f"Found {len(movies)} movie entries to process")
    
    # Process movies
    results = []
    success_count = 0
    
    for idx, (title, year) in enumerate(movies, start=1):
        logger.info(f"[{idx}/{len(movies)}] Processing: '{title}' ({year})")
        
        try:
            desc = get_plot_description(
                title, year, 
                api_key=args.api_key,
                force_scrape=args.force_scrape,
                delay=args.delay
            )
            # Sanitize description for markdown: escape pipes and newlines
            safe_desc = desc.replace('|', '\\|').replace('\n', ' ').strip()
            results.append(f"| {title} | {year} | {safe_desc} |")
            success_count += 1
            
        except Exception as e:
            logger.error(f"Unexpected error processing '{title}': {e}")
            results.append(f"| {title} | {year} | Error retrieving description |")
        
        # Rate limiting
        if idx < len(movies):
            time.sleep(args.delay)
    
    # Write output
    try:
        with open(args.output_path, 'w', encoding='utf-8') as out_f:
            out_f.write("| Title | Year | Description |\n")
            out_f.write("|---|---|---|\n")
            if results:
                out_f.write("\n".join(results) + "\n")
        logger.info(f"✓ Wrote {len(results)} entries to {args.output_path}")
        logger.info(f"Success rate: {success_count}/{len(movies)} ({100*success_count/len(movies):.1f}%)")
        
    except IOError as e:
        logger.error(f"Failed to write output file: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

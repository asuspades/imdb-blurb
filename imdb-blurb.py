#!/usr/bin/env python3
"""
Movie List Enrichment Script

Reads a Markdown-style movie list, searches IMDb for each title, and
appends a plot description. Produces a new Markdown table with descriptions.

Usage:
    python3 imdb_enrich.py --input list.txt --output list_with_descriptions.txt
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import argparse
import sys

# === Configuration ===
DEFAULT_DELAY = 1.5  # polite delay in seconds
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/102.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.imdb.com/'
}

ROW_PATTERN = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(\d{4})\s*\|")


def fetch_imdb_url(title, year):
    """Fetch IMDb URL for given movie title/year"""
    base_url = 'https://www.imdb.com/find'
    params = {
        'q': f"{title} {year}",
        's': 'tt',
        'ttype': 'ft',
        'ref_': 'nv_sr_sm'
    }

    try:
        resp = requests.get(base_url, params=params, headers=HEADERS)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"ERROR: IMDb search failed for '{title}' ({year}): {e}")
        return None

    soup = BeautifulSoup(resp.text, 'html.parser')
    results = soup.find_all('td', class_='result_text')
    print(f"DEBUG: {len(results)} results for '{title} ({year})'")

    for cell in results:
        text = cell.get_text(strip=True)
        if year in text:
            link = cell.find('a')
            if link and link.get('href'):
                path = link['href'].split('?')[0]
                url = f"https://www.imdb.com{path}"
                print(f"DEBUG: Matched URL: {url}")
                return url

    if results:
        first = results[0].find('a')
        if first and first.get('href'):
            path = first['href'].split('?')[0]
            url = f"https://www.imdb.com{path}"
            print(f"DEBUG: Fallback URL: {url}")
            return url

    print(f"DEBUG: No IMDb results for '{title}' ({year})'")
    return None


def scrape_imdb_description(imdb_url):
    """Scrape movie description from IMDb URL"""
    try:
        resp = requests.get(imdb_url, headers=HEADERS)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"ERROR: IMDb page request failed: {e}")
        return 'Description not found.', {}

    soup = BeautifulSoup(resp.text, 'html.parser')

    # Try extended plot first
    plot = soup.find('span', {'data-testid': 'plot-xl'})
    if plot:
        return plot.get_text(strip=True), {}

    # Fallback to meta description
    meta = soup.select_one('meta[name=description]')
    if meta and meta.get('content'):
        content = meta['content'].split('. Directed by')[0].strip()
        return content + '.', {}

    return 'Description not found.', {}


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Enrich movie list with IMDb descriptions.')
    parser.add_argument('--input', '-i', required=True,
                        help='Input Markdown movie list file')
    parser.add_argument('--output', '-o', required=True,
                        help='Output Markdown file with descriptions')
    parser.add_argument('--delay', '-d', type=float, default=DEFAULT_DELAY,
                        help='Delay between requests (seconds, default=1.5)')
    return parser.parse_args()


def main():
    args = parse_args()

    # Load input
    try:
        with open(args.input, encoding='utf-8') as f:
            lines = [l.rstrip() for l in f]
    except IOError as e:
        print(f"ERROR: Could not read input file: {e}")
        sys.exit(1)

    # Extract movie rows
    movies = []
    for line in lines:
        m = ROW_PATTERN.match(line)
        if m:
            movies.append((m.group(1).strip(), m.group(2)))
    print(f"Found {len(movies)} movie entries.")

    # Process movies
    results = []
    for idx, (title, year) in enumerate(movies, start=1):
        print(f"[{idx}/{len(movies)}] Processing '{title}' ({year})...")
        url = fetch_imdb_url(title, year)
        if not url:
            print(f"  Skipping '{title}' — URL not found.")
            continue

        desc, _ = scrape_imdb_description(url)
        results.append(f"| {title} | {year} | {desc} |")
        time.sleep(args.delay)

    # Write output
    try:
        with open(args.output, 'w', encoding='utf-8') as out_f:
            out_f.write("| Title | Year | Description |\n")
            out_f.write("|---|---|---|\n")
            out_f.write("\n".join(results))
    except IOError as e:
        print(f"ERROR: Could not write output file: {e}")
        sys.exit(1)

    print(f"\nDone! Wrote {len(results)} entries to {args.output}.")


if __name__ == '__main__':
    main()

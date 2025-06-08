#!/usr/bin/env python3
"""
Movie List Enrichment Script

Reads a Markdown-style movie list, searches IMDb for each title, and
appends a plot description. Produces a new Markdown table with descriptions.
"""

import requests
from bs4 import BeautifulSoup
import time
import re

# === Configuration ===
# Input file containing your movie table
txt_file = '/home/macrae/Videos/Movies/list.txt'
# Output file for the augmented table
output_file = '/home/macrae/Videos/Movies/list_with_descriptions.txt'

# HTTP headers to mimic a real browser request
headers = {
    'User-Agent': (
        'Mozilla/5.0 (X11; Linux x86_64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/102.0.0.0 Safari/537.36'
    ),
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.imdb.com/'
}

# Regex for table rows: | Title | Year |
ROW_PATTERN = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(\d{4})\s*\|")


def fetch_imdb_url(title, year):
    """
    Fetch the IMDb URL by querying IMDb's search endpoint.
    - Builds the search URL with title and year
    - Parses the results list for items matching the year
    - Falls back to the first result if no exact year match
    """
    base_url = 'https://www.imdb.com/find'
    params = {
        'q': f"{title} {year}",  # search terms
        's': 'tt',                # search titles only
        'ttype': 'ft',            # feature films
        'ref_': 'nv_sr_sm'         # search context ref
    }
    # Send the request
    search_resp = requests.get(base_url, params=params, headers=headers)
    if search_resp.status_code != 200:
        print(f"ERROR: HTTP {search_resp.status_code} for {title} search")
        return None

    # Parse search results
    soup = BeautifulSoup(search_resp.text, 'html.parser')
    results = soup.find_all('td', class_='result_text')
    # Debug: number of candidates found
    print(f"DEBUG: {len(results)} results for '{title} ({year})'")

    # Look for a result that includes the exact year
    for cell in results:
        text = cell.get_text(strip=True)
        if year in text:
            link = cell.find('a')
            if link and link['href']:
                path = link['href'].split('?')[0]
                url = f"https://www.imdb.com{path}"
                print(f"DEBUG: Matched URL: {url}")
                return url

    # Fallback: take the first result if available
    if results:
        first = results[0].find('a')
        if first and first.get('href'):
            path = first['href'].split('?')[0]
            url = f"https://www.imdb.com{path}"
            print(f"DEBUG: Fallback URL: {url}")
            return url

    print(f"DEBUG: No IMDb results for {title} ({year})")
    return None


def scrape_imdb_description(imdb_url):
    """
    Scrape the movie description from its IMDb page.
    - First tries the plot span (modern layout)
    - Falls back to the meta description tag
    Returns (description_text, {})
    """
    resp = requests.get(imdb_url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Attempt to retrieve the extended plot block
    plot = soup.find('span', {'data-testid': 'plot-xl'})
    if plot:
        text = plot.get_text(strip=True)
        return text, {}

    # Fallback: meta description content
    meta = soup.select_one('meta[name=description]')
    if meta and meta.get('content'):
        # Trim off trailing Director/Writers info if present
        content = meta['content'].split('. Directed by')[0].strip()
        return content + '.', {}

    # If all else fails
    return 'Description not found.', {}


def main():
    """
    Main workflow:
    1. Read input lines, filter movie rows
    2. For each title/year, fetch URL & description
    3. Collect and write out augmented Markdown table
    """
    # Load and parse the movie list
    with open(txt_file) as f:
        lines = [l.rstrip() for l in f]

    # Extract (title, year) tuples
    movies = []
    for line in lines:
        m = ROW_PATTERN.match(line)
        if m:
            movies.append((m.group(1).strip(), m.group(2)))
    print(f"Found {len(movies)} movie entries.")

    # Build the output entries
    results = []
    for idx, (title, year) in enumerate(movies, start=1):
        print(f"[{idx}/{len(movies)}] Processing '{title}' ({year})...")
        url = fetch_imdb_url(title, year)
        if not url:
            print(f"  Skipping '{title}' — URL not found.")
            continue

        desc, _ = scrape_imdb_description(url)
        results.append(f"| {title} | {year} | {desc} |")
        time.sleep(1)  # polite delay

    # Write the enhanced table
    with open(output_file, 'w') as out_f:
        out_f.write("| Title | Year | Description |\n")
        out_f.write("|---|---|---|\n")
        out_f.write("\n".join(results))

    print(f"\nDone! Wrote {len(results)} entries to {output_file}.")


if __name__ == '__main__':
    main()

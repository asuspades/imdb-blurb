# Movie List Enrichment Script

This repository contains a Python script that reads a Markdown-formatted movie list, searches IMDb for each title/year, and appends a plot description to generate an enriched table.

## Features

* **Automated IMDb lookup**: Uses IMDb’s "Find" endpoint to locate movie pages by title and year.
* **Dual description scraping**: Retrieves the full plot summary if available, otherwise falls back to IMDb’s metadata description.
* **Markdown output**: Produces a new Markdown table with an added **Description** column for easy sharing or GitHub display.
* **Robust parsing**: Regex-based filtering of table rows ensures only valid entries are processed.
* **Safe and configurable**: No hardcoded paths — pass input and output files as command-line arguments.
* **Polite scraping**: Configurable delay between requests to avoid overloading IMDb servers.
* **Debug logging**: Prints search results and URL matching steps for transparency.

## Prerequisites

* Python 3.7 or newer
* [Requests](https://pypi.org/project/requests/)
* [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)

Install dependencies using pip:

```bash
pip install requests beautifulsoup4
````

## Usage

1. **Prepare your input**: Create a Markdown file (e.g. `list.txt`) with a table of movies in `| Title | Year |` format.

Example:

```markdown
| Title | Year |
|---|---|
| Gentlemen Broncos | 2009 |
| Metropolis | 1927 |
```

2. **Run the script**:

```bash
python3 imdb_enrich.py --input list.txt --output list_with_descriptions.txt
```

Optional arguments:

* `--delay 1.5` — Delay (in seconds) between IMDb requests. Default is `1.5`.

Example with custom delay:

```bash
python3 imdb_enrich.py --input list.txt --output list_with_descriptions.txt --delay 2.0
```

3. **View your enriched table** in `list_with_descriptions.txt`. The output will contain the original columns plus a **Description** column:

```markdown
| Title | Year | Description |
|---|---|---|
| Gentlemen Broncos | 2009 | A teenager attends a fantasy writers' convention... |
| Metropolis | 1927 | In a futuristic city sharply divided between... |
```

## Notes

* The script uses a polite default delay of 1.5 seconds between IMDb requests to avoid overwhelming their servers. Please respect this if running on large lists.
* The **User-Agent** is configured to mimic a real browser and reduce request blocking.
* The script matches the year exactly if possible, otherwise falls back to the first search result.

## License

MIT License © MacRae Vallery

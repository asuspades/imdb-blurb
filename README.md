# Movie List Enrichment Script

This repository contains a Python script that reads a Markdown-formatted movie list, searches IMDb for each title/year, and appends a plot description to generate an enriched table.

## Features

* **Automated IMDb lookup**: Uses IMDb’s "Find" endpoint to locate movie pages by title and year.
* **Dual description scraping**: Retrieves the full plot summary if available, otherwise falls back to IMDb’s metadata description.
* **Markdown output**: Produces a new Markdown table with an added **Description** column for easy sharing or GitHub display.
* **Robust parsing**: Regex-based filtering of table rows ensures only valid entries are processed.
* **Debug logging**: Optional debug prints show search results and URL matching steps.

## Prerequisites

* Python 3.7 or newer
* [Requests](https://pypi.org/project/requests/)
* [BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)

Install dependencies using pip:

```bash
pip install requests beautifulsoup4
```

## Usage

1. **Prepare your input**: Create a Markdown file (`list.txt`) with a table of movies in `| Title | Year |` format.

2. **Configure paths**: Edit the `txt_file` and `output_file` variables at the top of `imdb_descriptions.py` to point to your input and desired output locations.

3. **Make executable (optional)**:

   ```bash
   chmod +x imdb_descriptions.py
   ```

4. **Run the script**:

   ```bash
   ./imdb_descriptions.py
   ```

   Or:

   ```bash
   python3 imdb_descriptions.py
   ```

5. **View your enriched table** in the `list_with_descriptions.txt` file, which will contain the original columns plus a **Description** column.

## Example

Input (`list.txt`):

```markdown
| Title | Year |
|---|---|
| Gentlemen Broncos | 2009 |
| Metropolis | 1927 |
```

Output (`list_with_descriptions.txt`):

```markdown
| Title | Year | Description |
|---|---|---|
| Gentlemen Broncos | 2009 | A teenager attends a fantasy writers' convention... |
| Metropolis | 1927 | In a futuristic city sharply divided between... |
```

## Configuration

* **User-Agent** and other HTTP headers are set in `headers` to mimic a real browser and reduce request blocking.
* **Delay**: The script pauses 1 second between requests (adjustable) to be polite to IMDb’s servers.
* **Regex**: Modify `ROW_PATTERN` if your table format differs.

## License

MIT License © Your Name

---

Feel free to contribute improvements or open issues if you encounter any problems.

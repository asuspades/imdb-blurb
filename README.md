# Movie List Enrichment Script

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-educational-yellow)](#)

> ⚠️ **Educational Tool Only** — Enrich Markdown movie lists with plot descriptions via OMDb API (preferred) or IMDb scraping (fallback, use with caution).

This Python script reads a Markdown-formatted movie list, searches for each title/year, and appends a plot description to generate an enriched table. Designed for personal archival, research, and learning about web APIs and HTML parsing.

---

## ⚠️ Important Legal & Ethical Notice

### IMDb Terms of Service
IMDb's [Conditions of Use](https://www.imdb.com/conditions) explicitly prohibit automated scraping:

> "You agree not to use any robot, spider, site search/retrieval application, or other automated device or process to access, 'scrape,' or copy any pages of the IMDb Properties..."

**Using the IMDb scraping fallback may violate these terms.** Potential consequences include IP blocking, account suspension, or legal action.

### ✅ Recommended: Use Official APIs Instead

| Service | Free Tier | Notes |
|---------|-----------|-------|
| **[OMDb API](https://www.omdbapi.com/)** | ✅ Yes (1k/day) | Preferred method; ToS-compliant; simple key-based auth |
| **[TMDB API](https://www.themoviedb.org/settings/api)** | ✅ Yes (40 req/10s) | Rich metadata; requires account registration |
| **[IMDb Datasets](https://imdb-public-datasets.s3.amazonaws.com/)** | ✅ Yes (bulk) | Non-commercial use; raw TSV files, not real-time |

**This script defaults to OMDb API when an API key is provided.** IMDb scraping is a fallback only and requires explicit opt-in.

---

## ✨ Features

- 🔑 **OMDb API First**: Uses official API when key provided; ToS-compliant and reliable
- 🔄 **Smart Fallback**: Optional IMDb scraping fallback with clear warnings (educational use only)
- 📝 **Markdown Output**: Generates clean, GitHub-ready tables with escaped special characters
- 🛡️ **Input Validation**: Path traversal protection, title length limits, year format checks
- ⏱️ **Rate Limiting**: Configurable delays with exponential backoff on failures
- 🪵 **Structured Logging**: Replaces debug prints with Python `logging` module; verbose mode available
- ♻️ **Resource Safety**: Timeouts on all requests; retry logic for transient failures

---

## 📦 Prerequisites

- Python 3.8 or newer
- `requests` and `beautifulsoup4` packages

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install requests>=2.28.0 beautifulsoup4>=4.11.0
```

---

## 🚀 Quick Start

### 1. Get an OMDb API Key (Recommended)
1. Visit https://www.omdbapi.com/apikey.aspx
2. Request a free key (no credit card required)
3. Copy your key for use below

### 2. Prepare Input File
Create a Markdown file (e.g., `movies.md`) with a table in this format:

```markdown
| Title | Year |
|---|---|
| Gentlemen Broncos | 2009 |
| Metropolis | 1927 |
| Cover_Art | 2023 |
```

> 💡 Tip: Only rows matching `| Title | YYYY |` format are processed.

### 3. Run the Script

#### Preferred: Using OMDb API
```bash
python3 imdb_enrich.py \
  --input movies.md \
  --output movies_enriched.md \
  --api-key YOUR_OMDB_KEY
```

#### Fallback: IMDb Scraping Only (Not Recommended)
```bash
python3 imdb_enrich.py \
  --input movies.md \
  --output movies_enriched.md \
  --force-scrape \
  --delay 3.0
```

> ⚠️ Using `--force-scrape` bypasses the API and uses IMDb scraping. Add `--delay 3.0` or higher to be polite to servers.

### 4. View Output
The generated file will contain:

```markdown
| Title | Year | Description |
|---|---|---|
| Gentlemen Broncos | 2009 | A teenager attends a fantasy writers' convention and discovers his story has been stolen. |
| Metropolis | 1927 | In a futuristic city sharply divided between the working class and the city planners... |
```

---

## ⚙️ Command-Line Options

| Argument | Short | Type | Default | Description |
|----------|-------|------|---------|-------------|
| `--input` | `-i` | `str` | *(required)* | Path to input Markdown file |
| `--output` | `-o` | `str` | *(required)* | Path for enriched output file |
| `--api-key` | `-k` | `str` | `None` | OMDb API key (strongly recommended) |
| `--delay` | `-d` | `float` | `2.0` | Seconds between requests (minimum 1.0 advised) |
| `--force-scrape` | — | `flag` | `False` | Force IMDb scraping even if API key provided ⚠️ |
| `--verbose` | `-v` | `flag` | `False` | Enable debug-level logging |
| `--help` | `-h` | — | — | Show help message and exit |

---

## 🔒 Security & Privacy

This script follows security best practices:

- ✅ **Path Validation**: Uses `pathlib.Path.resolve()` to prevent path traversal attacks
- ✅ **Input Sanitization**: Title length limits; markdown pipe characters escaped in output
- ✅ **No Credentials Logged**: API keys never written to logs or output files
- ✅ **Controlled Network Access**: All requests use timeouts and explicit headers
- ✅ **Transparent Operations**: Verbose mode shows exactly what is being fetched

> 🛡️ **Best Practice**: Run with `--verbose` first on a small test file to audit behavior before processing large lists.

---

## ⚠️ Known Limitations

| Limitation | Workaround/Note |
|------------|----------------|
| IMDb HTML structure changes | Scraping fallback may break; prefer OMDb API for stability |
| Rate limiting / IP blocks | Use `--delay 3.0+`; avoid parallel runs; monitor for HTTP 429 |
| No fuzzy title matching | Ensure input titles match IMDb exactly; consider pre-processing |
| Descriptions may be truncated | OMDb `plot=short` returns ~200 chars; use `plot=full` parameter if needed |
| No caching of results | Re-running re-fetches all entries; consider adding local cache in future versions |

---

## 🛠️ Troubleshooting

### ❌ "OMDb API returned 'Invalid API key'"
- Verify your key at https://www.omdbapi.com/apikey.aspx
- Ensure no extra whitespace: `--api-key "$(cat key.txt)"`
- Free keys have daily limits; wait 24h or upgrade

### ❌ "No results found for 'Title' (Year)"
- Check title spelling and year accuracy
- Try searching IMDb manually to verify the movie exists
- Some titles have multiple years (release vs. festival); try adjacent years

### ❌ Script hangs or times out
- Increase timeout: edit `DEFAULT_TIMEOUT` in script (advanced users)
- Check network connectivity and firewall rules
- Reduce batch size; process in chunks

### ❌ Output table is malformed
- Ensure input uses proper Markdown table syntax
- Descriptions with `|` characters are auto-escaped; check raw output if issues persist

### ❌ Getting HTTP 429 / "Too Many Requests"
- Increase `--delay` to 3.0 or higher
- Stop immediately and wait before retrying
- Switch to OMDb API with valid key for more reliable access

---

## 🤝 Contributing

Contributions welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feat/your-idea`
3. **Test thoroughly**:
   ```bash
   # Lint code
   flake8 imdb_enrich.py
   
   # Run with test data
   python3 imdb_enrich.py -i examples/input.md -o test_out.md -k TEST_KEY --verbose
   ```
4. **Follow Python best practices**:
   - Type hints for new functions
   - Docstrings in Google style
   - No hardcoded secrets or paths
5. **Submit a Pull Request** with:
   - Clear description of changes
   - Updated documentation if behavior changes
   - Tests for new logic (if applicable)

### Development Setup
```bash
# Clone and set up virtual environment
git clone https://github.com/asuspades/imdb-blurb.git
cd imdb-blurb
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Optional: install dev tools
pip install flake8 black mypy bandit
```

### Code Quality Checks
```bash
# Linting
flake8 imdb_enrich.py --max-line-length=100

# Type checking (if adding type hints)
mypy imdb_enrich.py

# Security audit
bandit -r .
```

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

```
MIT License

Copyright (c) 2026 MacRae Vallery

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

> 📌 **Note**: This license covers the *code only*. Data retrieved from OMDb, IMDb, TMDB, or other sources is subject to their respective terms of service and licensing.

---

## 📬 Support & Feedback

- 🐛 **Bug Reports**: [Open an Issue](https://github.com/asuspades/imdb-blurb/issues)
- 💡 **Feature Requests**: Use the [Discussions](https://github.com/asuspades/imdb-blurb/discussions) tab
- 🙋 **Questions**: Start a discussion or check the FAQ below

---

## ❓ FAQ

**Q: Why does the script warn about IMDb scraping?**  
A: IMDb's Terms of Service prohibit automated access. The warning ensures users make an informed choice. For production use, always prefer the OMDb API.

**Q: Can I use this for a commercial project?**  
A: The *code* is MIT-licensed, but *data sources* have separate terms. OMDb's free tier is for non-commercial use; commercial use requires a paid plan. Always verify data licensing for your use case.

**Q: How do I get more than 200 characters in plot descriptions?**  
A: The OMDb API supports `plot=full` for longer summaries. Edit the `fetch_omdb_plot()` function to add `'plot': 'full'` to the params dict.

**Q: Can I cache results to avoid re-fetching?**  
A: Not in the current version, but it's a great contribution idea! Consider adding a simple JSON cache keyed by `title+year`.

**Q: Does this work with TV shows?**  
A: The current regex and API params target films (`ttype=ft`). With minor modifications (removing `ttype` filter), it could support series—submit a PR if you implement this!

---

## 🗓️ Changelog

### [2.0.0] - 2026-04-02
- ✨ **New**: OMDb API as primary data source (ToS-compliant)
- ✨ **New**: `--api-key` and `--force-scrape` flags for flexible usage
- 🔧 **Improved**: Structured logging replaces debug prints; `--verbose` flag
- 🔧 **Improved**: Path validation, input sanitization, and markdown escaping
- 🔧 **Improved**: Retry logic with exponential backoff; request timeouts
- 📚 **Docs**: Added prominent legal notice, troubleshooting, and FAQ
- 🗑️ **Removed**: Hardcoded debug `print()` statements

### [1.0.0] - 2025-11-15
- Initial release
- IMDb scraping via `/find` endpoint and movie pages
- Markdown table parsing and output
- Configurable request delay

---

## 🌐 Related Projects

- [**OMDb API**](https://www.omdbapi.com/) — Official API for movie metadata
- [**IMDb Py**](https://github.com/alberanid/imdbpy) — Python interface to IMDb data (uses official datasets)
- [**TMDb Python**](https://github.com/cbrooker/python-tmdb3) — Client for The Movie Database API
- [**ocrmypdf**](https://ocrmypdf.readthedocs.io/) — Add OCR text layers to PDFs (complements archival workflows)

---

> 💡 **Pro Tip**: Combine with the [images-to-pdf](https://github.com/asuspades/images-to-pdf) script for a complete archival pipeline:
> ```bash
> # 1. Enrich movie list with descriptions
> python3 imdb_enrich.py -i watchlist.md -o watchlist_enriched.md -k YOUR_OMDB_KEY
> 
> # 2. Convert scanned cover art to optimized PDFs
> ./images-to-pdf.ps1 -InputFolder "C:\Covers\MyCollection"
> ```

---

*Made with ❤️ for film enthusiasts, researchers, and curious coders.*  
*Use responsibly. Respect data providers' terms. Happy watching! 🎬*  
[Report issues or suggest improvements](https://github.com/asuspades/imdb-blurb)

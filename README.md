# Volleyball Nations League Scraper

This Python project scrapes **Volleyball Nations League (VNL)** match results from [Flashscore](https://www.flashscore.com/), for both **women’s and men’s tournaments**, across multiple seasons.

It uses **Playwright** for headless browser automation and **Pandas** to store results in CSV and JSON formats.

---

## 📦 Features

- Scrapes match data for seasons 2018–2024
- Supports both **women** and **men** tournaments
- Extracts:
  - Match date
  - Home & away teams
  - Set-by-set scores
  - Total sets won
  - Match outcome (1 = home win, 0 = away win)
  - Match URL
- Outputs:
  - Individual CSV & JSON files per season
  - Merged files for all seasons per gender

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/jorgepanzera/vnl-scraper.git
cd vnl-scraper

### 2. Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt
playwright install

### 4. Run the Scrapper
python scrapVnlv2.py

After running, results will be saved in the vnl_results/ folder.
vnl_results/
├── vnl_women_2018.csv
├── vnl_women_2024.json
├── vnl_men_all.csv
└── ...

🧰 Built With
Python 3.9+
Playwright
Pandas
Flashscore (as the data source)

📄 License
This project is for educational and research use only. Please respect the terms of the data provider (Flashscore).


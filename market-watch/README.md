# MarketWatch Futures Scraper

This project scrapes **MarketWatch Futures Listings** and extracts detailed **futures contract data** (price, open interest, volume, etc.). The data is stored in **CSV and Parquet** formats for further analysis.

## 📌 Features
- Fetches **all futures listings** from MarketWatch.
- Extracts **detailed futures contract data**, including:
  - **Price** (€ or $)
  - **Latest change** (value & percentage)
  - **Open interest**
  - **Settlement price**
  - **Day range & 52-week range**
  - **Trading volume & 65-day average volume**
  - **Performance metrics** (5-day, 1-month, 3-month, YTD, 1-year)
  - **Open price**
  - **Timestamp (Last Updated)**
- Stores data in multiple formats:
  - **CSV**: `marketwatch_futures/futures_list.csv`, `marketwatch_futures_details/futures_details.csv`
  - **Parquet**: `marketwatch_futures_details/futures_details.parquet` (optimized for large-scale analysis)

## 🚀 Installation
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/mantryush/predikt_assignment.git
cd market-watch
```

### 2️⃣ Install Dependencies
Using `pip`:
```bash
pip install -r requirements.txt
```
Or using `poetry`:
```bash
poetry install
```

## 📜 Usage
### Run the Scraper
```bash
python main.py
```
This will:
1. Scrape all **MarketWatch futures listings**.
2. Extract **detailed data** for the first **3 futures contracts**.
3. Save the results in **CSV and Parquet** formats.

## 📂 Data Output
The scraper generates:
- **All futures listings** → `marketwatch_futures/futures_list.csv`
- **Detailed futures data** → `marketwatch_futures_details/futures_details.csv`
- **Optimized Parquet format** → `marketwatch_futures_details/futures_details.parquet`

## 📂 Project Structure
```
marketwatch_scraper/
│── marketwatch_futures/                    # Output directory (CSV, Parquet files) of futures list
│── marketwatch_futures_details/            # Output directory (CSV, Parquet files) of futures details
│── scraping/                # Scraper modules
│   ├── fetch_futures_list.py   # Fetches all futures listings
│   ├── fetch_future_details.py # Fetches price, open interest, etc.
│── pyproject.toml            # Dependency management (or use requirements.txt)
│── requirements.txt          # Alternative dependency manager
│── README.md                 # Documentation
│── main.py                   # Entry point script
│── .gitignore                # Ignore data and compiled files
```

## 🛠 Assumptions
- **MarketWatch pagination** has **35 pages**, and the scraper dynamically iterates through them.
- If **no data** is found for a futures contract, missing values are stored as `"N/A"`.
- **Cloudscraper** is used to bypass **Cloudflare restrictions**.
- Mimicing real browser request



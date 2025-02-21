# Energy Charts Scraper

This project gets electricity spot price data from the Energy-Charts API for Germany, France, and Belgium. The data is stored in CSV, JSON, and Parquet formats, with monthly averages calculated.

## 📌 Features
- Fetches **historical** electricity spot prices.
- Supports **three countries**: Germany, France, and Belgium.
- Saves data in **CSV, JSON, and Parquet** formats.
- Calculates **monthly average** spot prices.

## 🚀 Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/battulga-batman/predikt.git
   cd energy-chart
   ```

2. Install dependencies using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

   Or use `poetry`:
   ```bash
   poetry install
   ```

## 📜 Usage
### How to Run the Script
Run the script using:
```bash
python src/main.py
```

### Example Output
The script will fetch electricity spot price data and store the results in the `data/` directory.

## 📂 Data Output
The script generates:
- **Raw spot prices**: `data/spot_prices_Germany.csv`
- **Monthly averages**: `data/monthly_avg_spot_prices_Germany.csv`

## 🛠️ Project Structure
```
energy-chart/
│── data/                    # Output directory (CSV, JSON, Parquet files)
│── src/                     # Source code directory
│   ├── main.py              # Entry point script
│   ├── scraper.py           # Handles API calls
│   ├── transform.py         # Handles data transformations
│   ├── storage.py           # Handles saving data
│   ├── config.py            # Constants and settings
│── requirements.txt         # Python dependencies
│── pyproject.toml           # Alternative dependency manager
│── README.md                # Documentation
│── .gitignore               # Ignore data and compiled files
```

## ⚙️ Assumptions
- The API provides **hourly** spot prices, which are aggregated **monthly**.

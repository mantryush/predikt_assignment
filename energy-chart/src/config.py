import os
from datetime import datetime

OUTPUT_DIR = "data"
COUNTRIES = {"DE-LU": "Germany", "FR": "France", "BE": "Belgium"}
BASE_URL = "https://api.energy-charts.info"
END_DATE = datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ')
CHUNK_SIZE = 365

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)
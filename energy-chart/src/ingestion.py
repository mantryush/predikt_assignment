import requests
from config import BASE_URL

def fetch_data(url):
    """Sends an API request and returns the response JSON."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

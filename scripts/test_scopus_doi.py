from pathlib import Path
from dotenv import load_dotenv
import os
import requests

env_path = Path(r"D:\Documents\E-library\Vowan_Database\Valentine_Site\.env")
load_dotenv(env_path)

API_KEY = os.getenv("ELSEVIER_API_KEY")

DOI = "10.1016/j.compedu.2020.103907"  # replace with one DOI from your Excel

url = "https://api.elsevier.com/content/abstract/citation-count"
headers = {
    "X-ELS-APIKey": API_KEY,
    "Accept": "application/json"
}
params = {"doi": DOI}

response = requests.get(url, headers=headers, params=params, timeout=30)

print("Status code:", response.status_code)
print(response.text[:2000])
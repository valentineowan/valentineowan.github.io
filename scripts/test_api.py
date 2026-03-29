from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path(r"D:\Documents\E-library\Vowan_Database\Valentine_Site\.env")
load_dotenv(env_path)

API_KEY = os.getenv("ELSEVIER_API_KEY")

print("API key loaded:", bool(API_KEY))
print("API key starts with:", API_KEY[:4] if API_KEY else None)
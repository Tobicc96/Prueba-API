
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Cargar la configuración desde el archivo .env
load_dotenv(Path(__file__).with_name(".env"))

API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError("No se encontró YOUTUBE_API_KEY en el archivo .env")

url = "https://www.googleapis.com/youtube/v3/videos"

params = {
    "part": "statistics",
    "id": "nTI1WIz8r5M",
    "key": API_KEY
}

response = requests.get(url, params=params, timeout=15)
response.raise_for_status()

print("Estado HTTP:", response.status_code)
print(response.json())

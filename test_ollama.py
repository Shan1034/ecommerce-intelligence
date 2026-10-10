
import requests

url = "http://localhost:11434/api/generate"

payload = {
    "model": "qwen2.5:3b",
    "prompt": "Explain profit margin in simple business terms.",
    "stream": False
}

response = requests.post(url, json=payload, timeout=120)
response.raise_for_status()

print(response.json()["response"])

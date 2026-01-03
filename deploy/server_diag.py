
import requests
import os
import sys

# Try to read .env manually to check for corruption
print("--- Checking .env ---")
try:
    with open(".env", "r") as f:
        for line in f:
            if "N8N_TELEGRAM_WEBHOOK_URL" in line:
                print(f"Found Line: {line.strip()}")
except FileNotFoundError:
    print(".env not found!")

print("\n--- Testing Backend API ---")
try:
    payload = {"message": "Direct Test from Server Script", "level": "success"}
    print(f"Sending: {payload}")
    r = requests.post("http://localhost:8001/api/notify/telegram", json=payload, timeout=5)
    print(f"Response Code: {r.status_code}")
    print(f"Response Body: {r.text}")
except Exception as e:
    print(f"Error: {e}")

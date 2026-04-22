import requests

url = "http://127.0.0.1:8000/generate/text"
payload = {
    "text": "This is a test.",
    "format_type": "linkedin",
    "run_brand_check": False
}

try:
    print("Sending request...")
    response = requests.post(url, json=payload, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except requests.exceptions.Timeout:
    print("ERROR: Request timed out after 10 seconds")
except requests.exceptions.ConnectionError as e:
    print(f"ERROR: Connection failed - {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__} - {e}")

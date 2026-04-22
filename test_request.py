import requests
import json

url = 'http://127.0.0.1:8000/generate/text'
payload = {
    'text': 'This is a test.',
    'format_type': 'linkedin',
    'run_brand_check': False
}

try:
    response = requests.post(url, json=payload, timeout=30)
    print('Status Code:', response.status_code)
    print('\nResponse Headers:')
    for key, value in response.headers.items():
        print(f'  {key}: {value}')
    print('\nResponse Body:')
    print(response.text)
except requests.exceptions.Timeout:
    print('Error: Request timed out')
except requests.exceptions.ConnectionError as e:
    print('Error: Connection failed -', str(e))
except Exception as e:
    print('Error:', type(e).__name__)
    print('Message:', str(e))

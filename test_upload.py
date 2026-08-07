import requests

url = "http://127.0.0.1:8002/api/v1/files/upload"
files = {'file': open('test.csv', 'rb')}

response = requests.post(url, files=files)
print(f"Status Code: {response.status_code}")
import json
print(json.dumps(response.json(), indent=2))

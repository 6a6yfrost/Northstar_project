import requests
import json

# Test the chat API
url = "http://localhost:5000/api/chat"
data = {"message": "order status"}

try:
    response = requests.post(url, json=data)
    print("Status Code:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2))
except Exception as e:
    print("Error:", str(e))

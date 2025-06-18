import requests

url = "http://localhost:5000/register"
data = {"hostname": "test-host"}
resp = requests.post(url, json=data)
print("Status:", resp.status_code)
print("Réponse:", resp.text)
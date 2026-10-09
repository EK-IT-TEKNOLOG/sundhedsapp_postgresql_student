import requests

token = requests.post("http://127.0.0.1:5000/token/1")
print(str(token.json()["token"]))

url = "http://127.0.0.1:5000/health_data"

# API header with token autenticate
headers = {
    "accept" : "application/json",
    "Authorization" : token.json()["token"]
}

response = requests.get(url, headers=headers)

print(response.text)
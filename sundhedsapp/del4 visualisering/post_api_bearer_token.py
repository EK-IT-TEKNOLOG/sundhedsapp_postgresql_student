import requests

# TODO plot med pandas
# https://www.geeksforgeeks.org/pandas/how-to-plot-a-dataframe-using-pandas/
import pandas as pd
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

df = pd.DataFrame(response.text)
print(df)
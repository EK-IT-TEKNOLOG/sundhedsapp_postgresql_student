import requests

response = requests.get("http://127.0.0.1:5000/health_data")
print(response.json())

patient = {
    "first_name" : input("first_name\n>"),
    "last_name" : input("last_name\n>"),
    "age" : int(input("age")),
    "bloodtype" : input("bloodtype\n>"),
    "allergies" : input("allergies\n>"),
}

print(patient)

requests.post("http://127.0.0.1:5000/add_patient", json=patient)
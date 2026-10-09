import yaml

def read_yaml():
    with open("patient.yml") as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)
        return yaml_data

d = {
    "first_name" : "Lone",
    "last_name" : "Kellerman",
    "age" : 66,
    "blood_type" : "A+",
    "allergies" : "Peanuts",
}

def write_yaml():
    data = read_yaml()
    new = data.get("patients").get("id")
    new.setdefault(len(new) + 1, d)
    with open("patient.yml", "w") as y:
        yaml.dump(data, y)
    return new

print(write_yaml())
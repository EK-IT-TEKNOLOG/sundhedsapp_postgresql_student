import yaml
from flask import current_app
from apiflask import APIFlask, Schema, HTTPTokenAuth, abort
from apiflask.fields import Integer, String
from authlib.jose import jwt, JoseError
import secrets 

app = APIFlask(__name__)
auth = HTTPTokenAuth(scheme="Bearer")
app.config['SECRET_KEY'] = secrets.token_bytes(32)

class PatientIn(Schema):
    first_name = String(required=True)
    last_name = String(required=True)
    age = Integer()
    bloodtype = String(required=True)
    allergies = String(required=True)

class User:
    def __init__(self, id : int, secret : str):
        self.id = id
        self.secret = secret
    
    def get_token(self):
        header = {'alg' : 'HS256'}
        payload = {'id' : self.id}
        return jwt.encode(header, payload, current_app.config['SECRET_KEY']).decode()

class Token(Schema):
    token = String()

users = [
    User(1, "Kevin"),
    User(2, "Malene"),
    User(3, "Charlie"),
]

def get_user_by_id(id: int) -> User | None:
    return tuple(filter(lambda u: u.id == id, users))[0]


def read_yaml():
    with open("patient.yml") as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)
        return yaml_data


def write_yaml(data):
    with open("patient.yml", "w") as y:
        yaml.dump(data, y)


@app.post('/add_patient')
@app.input(PatientIn)
def add_new_patient(json_data):
    """
    Adds new patient to the YAML file
    """
    print(json_data)
    data = read_yaml()
    new = data.get("patients").get("id")
    new.setdefault(len(new) + 1, json_data)
    write_yaml(data)
    return {'message': 'created'}, 201


@app.get('/health_data')
@app.auth_required(auth)
def get_health_data():
    """
    Get all data about patients
    """
    return read_yaml()

@auth.verify_token
def verify_token(token : str) -> User | None:
    try:
        data = jwt.decode(
            token.encode('ascii'),
            current_app.config['SECRET_KEY'],
        )
        id = data['id']
        user = get_user_by_id(id)
    except JoseError:
        return None
    except IndexError:
        return None
    return user

@app.post('/token/<int:id>')
@app.output(Token)
def get_token(id : int):
    if get_user_by_id(id) is None:
        abort(404)
    return {'token' : f'Bearer {get_user_by_id(id).get_token()}'}
           
@app.get('/name/<int:id>')
@app.auth_required(auth)
def get_secret(id):
    return auth.current_user.secret
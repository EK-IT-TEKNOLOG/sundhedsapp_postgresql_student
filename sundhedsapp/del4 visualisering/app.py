import yaml
from flask import current_app, render_template
from apiflask import APIFlask, Schema, HTTPTokenAuth, abort
from apiflask.fields import Integer, String
from authlib.jose import jwt, JoseError
import secrets 

# https://www.geeksforgeeks.org/python/create-a-bar-chart-from-a-dataframe-with-plotly-and-flask/
import pandas as pd
import json
import plotly
import plotly.express as px

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

@app.route('/')
def bar_with_plotly():
  
   # Students data available in a list of list
    p = read_yaml()
    #print(p.get('patients').get('id'))
    patient_list = []
    for patient in p.get('patients').get('id'):
        inner_list = []
        print(p.get('patients').get('id').get(patient))

        inner_list.append(p.get('patients').get('id').get(patient).get("first_name"))
        inner_list.append(p.get('patients').get('id').get(patient).get("age"))
        inner_list.append(p.get('patients').get('id').get(patient).get("blood_type"))
        patient_list.append(inner_list)
    print(patient_list)
    # Convert list to dataframe and assign column values
    df = pd.DataFrame(patient_list,
                      columns=['Name', 'Age', 'Blood type'],
                      index=['a', 'b', 'c', 'd'])
    
    # Create Bar chart
    fig = px.bar(df, x='Name', y='Age', color='Blood type', barmode='group')
    
    # Create graphJSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Use render_template to pass graphJSON to html
    return render_template('plots.html', graphJSON=graphJSON)

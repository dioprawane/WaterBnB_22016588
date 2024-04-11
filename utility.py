import json
from jsonschema import validate
import os

def is_json(message):
    try:
        json.loads(message)
        return True
    except ValueError:
        return False
    

def validate_json(json_data):
    current_directory = os.getcwd()
    try:
        with open(current_directory+'/validator/shema.json', 'r') as file:
            schema = json.load(file)
        validate(instance=json_data, schema=schema)
        return True
    except Exception as e:
        print(f"Validation error: {e}")
        return False
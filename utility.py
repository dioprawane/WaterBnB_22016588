import json
from jsonschema import validate, Draft7Validator
import os
from flask import Flask
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

def is_json(message):
    try:
        json.loads(message)
        return True
    except ValueError:
        return False
    

def validate_json(json_data,debug):
    current_directory = os.getcwd()
    schema_path = os.path.join(  'validator', 'a')
    if not os.path.exists('./validator/shema.json'):
        print("Le fichier de schéma n'existe pas.")
        print(schema_path)
        contenu = os.listdir('./validator')
        print(contenu)
        return False
    try:
        with open('./validator/shema.json', 'r') as file:
            schema = json.load(file)
        
        validate(instance=json_data, schema=schema)
        print('Validator is Okay !') if debug else None
        return True
    except Exception as e:
        print(f"Erreur de validation : {e}")
        return False
    
def ping_mongodb(client):
    try:
        
        # Try to connect to the MongoDB server
        return "MongoDB is reachable."
    except ServerSelectionTimeoutError:
        return "Failed to connect to MongoDB."

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
    
# Function to validate the JSON data, if is not valid return a False else return a True
def validate_json(json_data,debug):
    # Check if the schema file exists is utils to debug
    if not os.path.exists('./validator/shema.json'):
        print("Le fichier de schéma n'existe pas.")
        contenu = os.listdir('./validator')
        print(contenu)
        return False
    # Load the schema file 
    with open('./validator/shema.json', 'r') as file:
            schema = json.load(file)
    try:
        # Test the JSON data with the schema
        validate(instance=json_data, schema=schema)
        print('Validator is Okay !') if debug else None
        return True
    except Exception as e:
        print(f"Erreur de validation : {e}") if debug else None
        return False
    
def ping_mongodb(client):
    try:
        
        # Try to connect to the MongoDB server
        return "MongoDB is reachable."
    except ServerSelectionTimeoutError:
        return "Failed to connect to MongoDB."
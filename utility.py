import json
from jsonschema import validate
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
    
def ping_mongodb(client):
    try:
        # Try to connect to the MongoDB server
        print(client)
        return "MongoDB is reachable."
    except ServerSelectionTimeoutError:
        return "Failed to connect to MongoDB."

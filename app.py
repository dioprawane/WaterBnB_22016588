import json
#from jsonschema import validate
import csv
import os  # Ajoutez cette importation en haut de votre fichier
import utility
from jsonschema import validate

from flask import request
from flask import jsonify
from flask import Flask
from flask import session
from flask import render_template
from datetime import datetime
#https://python-adv-web-apps.readthedocs.io/en/latest/flask.html

#https://www.emqx.com/en/blog/how-to-use-mqtt-in-flask
from flask_mqtt import Mqtt
from flask_pymongo import PyMongo
from pymongo import MongoClient

import logging

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Initialisation :  Mongo DataBase

# Connect to Cluster Mongo : attention aux permissions "network"/MONGO  !!!!!!!!!!!!!!!!
ADMIN=True # Faut etre ADMIN/mongo pour ecrire dans la base
#client = MongoClient("mongodb+srv://menez:i.....Q@cluster0.x0zyf.mongodb.net/?retryWrites=true&w=majority")
#client = MongoClient("mongodb+srv://logincfsujet:pwdcfsujet@cluster0.x0zyf.mongodb.net/?retryWrites=true&w=majority")
#client = MongoClient("mongodb+srv://visitor:doliprane@cluster0.x0zyf.mongodb.net/?retryWrites=true&w=majority")

mot_de_passe_mongo = os.getenv('MotDePasseMongoDB')  # Utilisez os.getenv pour récupérer la valeur
#client = MongoClient("mongodb+srv://borreani_iot:" + mot_de_passe_mongo + "@cluster0.kcb93lq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient("mongodb+srv://borreani_iot:" + "SuperTheo83" + "@cluster0.kcb93lq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")



#-----------------------------------------------------------------------------
# Looking for "WaterBnB" database in the cluster
#https://stackoverflow.com/questions/32438661/check-database-exists-in-mongodb-using-pymongo
dbname= 'WaterBnB'
dbnames = client.list_database_names()
if dbname in dbnames: 
    print(f"{dbname} is there!")

else:
    print("YOU HAVE to CREATE the db !\n")

db = client.WaterBnB

#-----------------------------------------------------------------------------
# Looking for "users" collection in the WaterBnB database
collname= 'users'
collname2 = db['piscines']
collnames = db.list_collection_names()
if collname in collnames: 
    print(f"{collname} is there!")
if collname2 in collnames: 
    print(f"{collname2} is there!")
else:
    print(f"YOU HAVE to CREATE the {collname} collection !\n")
    print(f"YOU HAVE to CREATE the {collname2} collection !\n")
    
userscollection = db.users
piscinescollection = db['piscines']

# Ensure that the MongoDB collections exist and handle them correctly
if 'users' not in db.list_collection_names():
    db.create_collection('users')
if 'piscines' not in db.list_collection_names():
    db.create_collection('piscines')


#-----------------------------------------------------------------------------
# import authorized users .. if not already in ?
if ADMIN :
    userscollection.delete_many({})  # empty collection
    excel = csv.reader(open("usersM1_2024.csv")) # list of authorized users
    for l in excel : #import in mongodb
        ls = (l[0].split(';'))
        #print(ls)
        if userscollection.find_one({"name" : ls[0]}) ==  None :
            userscollection.insert_one({"name": ls[0], "num": ls[1]})
    

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Initialisation :  Flask service
app = Flask(__name__)

# Notion de session ! .. to share between routes !
# https://flask-session.readthedocs.io/en/latest/quickstart.html
# https://testdriven.io/blog/flask-sessions/
# https://www.fullstackpython.com/flask-globals-session-examples.html
# https://stackoverflow.com/questions/49664010/using-variables-across-flask-routes
app.secret_key = 'BAD_SECRET_KEY'
  
#-----------------------------------------------------------------------------
@app.route('/')
def hello_world():
    return render_template('index.html') #'Hello, World!'

#Test with =>  curl https://waterbnbf.onrender.com/

#-----------------------------------------------------------------------------
"""
#https://stackabuse.com/how-to-get-users-ip-address-using-flask/
@app.route("/ask_for_access", methods=["POST"])
def get_my_ip():
    ip_addr = request.remote_addr
    return jsonify({'ip asking ': ip_addr}), 200

# Test/Compare with  =>curl  https://httpbin.org/ip

#Proxies can make this a little tricky, make sure to check out ProxyFix
#(Flask docs) if you are using one.
#Take a look at request.environ in your particular environment :
@app.route("/ask_for_access", methods=["POST"])
def client():
    ip_addr = request.environ['REMOTE_ADDR']
    return '<h1> Your IP address is:' + ip_addr
"""

@app.route("/users")
def lists_users(): # Liste des utilisateurs déclarés
    """
    curl https://waterbnbf.onrender.com/users
    """
    todos = userscollection.find()
    return jsonify([todo['name'] for todo in todos])

# Initialisation MQTT
app.config['MQTT_BROKER_URL'] =  "test.mosquitto.org"
app.config['MQTT_BROKER_PORT'] = 1883
#app.config['MQTT_USERNAME'] = ''  # Set this item when you need to verify username and password
#app.config['MQTT_PASSWORD'] = ''  # Set this item when you need to verify username and password
app.config['MQTT_KEEPALIVE'] = 5  # Set KeepAlive time in seconds
app.config['MQTT_TLS_ENABLED'] = False  # If your broker supports TLS, set it True

topicname = "uca/iot/piscine"
topicname2 = "uca/M1/iot/etat2201"
mqtt_client = Mqtt(app)

@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt_client.subscribe(topicname) # subscribe topic
       mqtt_client.subscribe(topicname2)
   else:
       print('Bad connection. Code:', rc)


@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, msg):
    global topicname
    global topicname2
    nbrValueMax = 1000 # max number of values in the tab_requests
    debug = False  # True for debug mode, if you want to see all the messages
    nowDate = datetime.today().replace(microsecond=0)

    data = dict(
        topic=msg.topic,
        payload=msg.payload.decode()
    )
    #    print('Received message on topic: {topic} with payload: {payload}'.format(**data))
    print("\n msg.topic = {}".format(msg.topic)) if debug else None
    print("\n topicname = {}".format(topicname)) if debug else None
    print("\n topicname2 = {}".format(topicname2)) if debug else None

    try:
        data = json.loads(msg.payload.decode())
        print("Received message on topic {}: {}".format(msg.topic, data))  if debug else None
        if (msg.topic == topicname2) :
            # Process the message appropriately
            process_piscine_status(data)
    except json.JSONDecodeError as e:
        print("Error decoding JSON: {}".format(e)) if debug else None
    
    if (msg.topic == topicname) : # cf https://stackoverflow.com/questions/63580034/paho-updating-userdata-from-on-message-callback
        decoded_message =str(msg.payload.decode("utf-8"))
        print("\x1b[32m"+decoded_message+"\x1b[30m") if debug else None
        # first step check if the message is a json
        if(utility.is_json(decoded_message) and decoded_message != "" and decoded_message != "{}"):
            dic = json.loads(decoded_message) # from string to dict
            print("\x1b[31m"+decoded_message+"\x1b[30m")  if debug else None
            # second step check if the json message is valid with use the JSON schema
            if(utility.validate_json(dic, debug)):
                print("\n Dictionnary  received = {}".format(dic)) if debug else None
                ident = dic["info"]["ident"] # Qui a publié ?
                data = piscinescollection.find_one({"info.ident": ident});# data associé a qui a publié
                # if the data already exist, we update the tab_requests
                if(data != None ):
                    print("data exist !!!") if debug else None
                    # check if the number of requests is not too, big else pop all the oldest requests
                    while (len(data["tab_requests"]) > nbrValueMax):
                        data = piscinescollection.find_one({"info.ident": ident});# data associé a qui a publié
                        piscinescollection.update_one({"info.ident": ident}, {"$pop": {"tab_requests": -1}})
                    nouvelle_valeur =  { 
                        "date":nowDate,
                        "statuts":dic["status"],
                        "piscine":dic["piscine"]
                    }
                    piscinescollection.update_one({"info.ident": ident}, {"$push": {"tab_requests": nouvelle_valeur}})
                    piscinescollection.update_one({"info.ident": ident}, {"$set": {"info": data["info"], "location": data["location"], "regul": data["regul"], "net": data["net"], "reporthost": data["reporthost"]}})
                # else we create a new data
                else:
                    piscinescollection.insert_one({
                        "nbr_request": 0,
                        "info": dic["info"],
                        "location": dic["location"],  # Directly use the dictionary instead of converting it
                        "regul": dic["regul"],
                        "net": dic["net"],
                        "reporthost": dic["reporthost"],
                        "tab_requests": [{
                            "date": nowDate,
                            "statuts": dic["status"],
                            "piscine": dic["piscine"] 
                        }],
                        "tab_demandes": [],
                    })

                    
def process_piscine_status(data):
    debug = False  # True for debug mode, if you want to see all the messages
    if isinstance(data, dict) and "etatPiscine" in data:
        etat = data['etatPiscine']
        # Assume additional processing here
        print("Processing Piscine State: {}".format(etat)) if debug else None

@app.route("/open", methods=['GET', 'POST'])
def openthedoor():
    idu = request.args.get('idu')
    idswp = request.args.get('idswp')
    user = userscollection.find_one({"name": idu})
    

    if user and user.get('etatPiscine', 1) == 1:
        mqtt_client.publish(topicname2, json.dumps({"etatPiscine": 0}))
        try:
            nouvelle_valeur =  { 
                            "authorize":True,
                            "date":datetime.today().replace(microsecond=0),
                            "user":user,
                        }
            piscinescollection.update_one({"info.ident": idswp}, {"$push": {"tab_demandes": nouvelle_valeur}})
        except Exception as e:
            print("Error in open the door")
        return render_template('index.html', idu=idu, idswp=idswp, granted="YES")
    else:
        mqtt_client.publish(topicname2, json.dumps({"etatPiscine": 0}))
        try:
            nouvelle_valeur =  { 
                            "authorize":True,
                            "date":datetime.today().replace(microsecond=0),
                            "user":user,
                        }
            piscinescollection.update_one({"info.ident": idswp}, {"$push": {"tab_demandes": nouvelle_valeur}})
        except Exception as e:
            print("Error in open the door")
        return render_template('index.html', idu=idu, idswp=idswp, granted="NO")

# Test with => curl -X POST https://waterbnbf.onrender.com/open?who=gillou
# Test with => curl https://waterbnbf.onrender.com/open?who=gillou

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%        


@app.route('/users', methods=['GET'])
def list_users():
    users = list(userscollection.find({}, {'_id': 0, 'name': 1}))  # Exclude the MongoDB ID from results
    return jsonify(users)

@app.route('/publish', methods=['POST'])
def publish_message():

    content_type = request.headers.get('Content-Type')
    print("\n Content type = {}".format(content_type))
    request_data = request.get_json()
    topic = request_data.get('topic', 'default/topic')
    message = request_data.get('msg', '{}')
    print("\n topic = {}".format(request_data['topic']))
    result = mqtt_client.publish(topic, json.dumps(message))
    return jsonify({'code': result.rc})
    



# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Use logging
logging.info("This is an info message")

#%%%%%%%%%%%%%  main driver function
if __name__ == '__main__':
    
    # run() method of Flask class runs the application 
    # on the local development server.
    app.run(debug=False) #host='127.0.0.1', port=5000)
    

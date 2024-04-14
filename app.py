import json
from jsonschema import validate
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
collnames = db.list_collection_names()
if collname in collnames: 
    print(f"{collname} is there!")
else:
    print(f"YOU HAVE to CREATE the {collname} collection !\n")
    
userscollection = db.users
piscinescollection = db.piscines

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

# Envoie etat de la piscine vers l'ESP
def envoyer_etat_piscine(etat):
    """
    Envoie l'état de la piscine à l'ESP via MQTT.
    'etat' peut être 0 (disponible), 1 (occupée) ou 2 (accès refusé).
    """
    sujet = "uca/iot/piscine/etat22016588"  # Assurez-vous que ce sujet correspond à celui attendu par votre ESP
    message = json.dumps({"etatPiscine": etat})
    resultat = mqtt_client.publish(sujet, message)
    print(f"Envoi MQTT {sujet} avec le message {message}, résultat: {resultat}")



#https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For
#If a request goes through multiple proxies, the IP addresses of each successive proxy is listed.
# voir aussi le parsing !

# @app.route("/open", methods= ['GET', 'POST'])
# # @app.route('/open') # ou en GET seulement
# def openthedoor():
#     idu = request.args.get('idu') # idu : clientid of the service
#     idswp = request.args.get('idswp')  #idswp : id of the swimming pool
#     session['idu'] = idu
#     session['idswp'] = idswp
#     print("\n Peer = {}".format(idu))

#     # ip addresses of the machine asking for opening
#     ip_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)

#     if userscollection.find_one({"name" : idu}) !=  None:
#         granted = "YES"
#     else:
#         granted = "NO"
#     #return  jsonify({'idu' : session['idu'], 'idswp' : session['idswp'], "granted" : granted}), 200
#     # Utilisez render_template pour envoyer les données à index.html
#     return render_template('index.html', idu=session['idu'], idswp=session['idswp'], granted=granted)

# Supposons que cette variable est définie quelque part dans votre application
# 0 = disponible, 1 = occupée
# Supposons que cette variable est définie quelque part au niveau global de votre application
# 0 = disponible, 1 = occupée
@app.route("/open", methods=['GET', 'POST'])
def openthedoor():
    idu = request.args.get('idu')
    idswp = request.args.get('idswp')
    session['idu'] = idu
    session['idswp'] = idswp
    
    utilisateur_autorise = userscollection.find_one({"name": idu}) is not None
    
    try:
        with open('etat_piscine.txt', 'r') as f:
            # Assurez-vous que le bloc suivant est correctement indenté
            etatPiscine = int(f.read().strip())
    except FileNotFoundError:
        etatPiscine = 0  # Assumer la piscine disponible si le fichier n'existe pas

    piscine_disponible = etatPiscine == 0

    if utilisateur_autorise and piscine_disponible:
        granted = "YES"
        envoyer_etat_piscine(1)
    else:
        granted = "NO"
        envoyer_etat_piscine(2)

    return render_template('index.html', idu=session['idu'], idswp=session['idswp'], granted=granted)





# Test with => curl -X POST https://waterbnbf.onrender.com/open?who=gillou
# Test with => curl https://waterbnbf.onrender.com/open?who=gillou

@app.route("/users")
def lists_users(): # Liste des utilisateurs déclarés
    """
    curl https://waterbnbf.onrender.com/users
    """
    todos = userscollection.find()
    return jsonify([todo['name'] for todo in todos])

@app.route('/publish', methods=['POST'])
def publish_message():
    """
    mosquitto_sub -h test.mosquitto.org -t gillou
    mosquitto_pub -h test.mosquitto.org -t gillou -m tutu
    curl -X POST -H Content-Type:application/json -d "{\"topic\":\"gillou\",\"msg\":\"hello\"}"  https://waterbnbf.onrender.com/publish
    """
    content_type = request.headers.get('Content-Type')
    print("\n Content type = {}".format(content_type))
    request_data = request.get_json()
    print("\n topic = {}".format(request_data['topic']))
    
    publish_result = mqtt_client.publish(request_data['topic'], request_data['msg'])
    return jsonify({'code': publish_result[0]})

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%        
# Initialisation MQTT
app.config['MQTT_BROKER_URL'] =  "test.mosquitto.org"
app.config['MQTT_BROKER_PORT'] = 1883
#app.config['MQTT_USERNAME'] = ''  # Set this item when you need to verify username and password
#app.config['MQTT_PASSWORD'] = ''  # Set this item when you need to verify username and password
#app.config['MQTT_KEEPALIVE'] = 5  # Set KeepAlive time in seconds
app.config['MQTT_TLS_ENABLED'] = False  # If your broker supports TLS, set it True

topicname = "uca/iot/piscine"
mqtt_client = Mqtt(app)

@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt_client.subscribe(topicname) # subscribe topic
   else:
       print('Bad connection. Code:', rc)


# @mqtt_client.on_message()
# def handle_mqtt_message(client, userdata, msg):
#     global topicname
    
#     data = dict(
#         topic=msg.topic,
#         payload=msg.payload.decode()
#     )
#     #    print('Received message on topic: {topic} with payload: {payload}'.format(**data))
#     print("\n msg.topic = {}".format(msg.topic))
#     print("\n topicname = {}".format(topicname))
    
#     if (msg.topic == topicname) : # cf https://stackoverflow.com/questions/63580034/paho-updating-userdata-from-on-message-callback
#         decoded_message =str(msg.payload.decode("utf-8"))
#         #print("\ndecoded message received = {}".format(decoded_message))
#         dic =json.loads(decoded_message) # from string to dict
#         print("\n Dictionnary  received = {}".format(dic))

#         who = dic["info"]["ident"] # Qui a publié ?
#         t = dic["status"]["temperature"] # Quelle température ?

@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, msg):
    global topicname
    nbrValueMax = 1000 # max number of values in the tab_requests
    debug = True  # True for debug mode, if you want to see all the messages
    nowDate = datetime.today().replace(microsecond=0)
    data = dict(
        topic=msg.topic,
        payload=msg.payload.decode()
    )
    #    print('Received message on topic: {topic} with payload: {payload}'.format(**data))
    print("\n msg.topic = {}".format(msg.topic)) if debug else None
    print("\n topicname = {}".format(topicname)) if debug else None
    
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
                # else we create a new data
                else:
                    piscinescollection.insert_one({
                        "nbr_request":0,
                        "info":dic["info"],
                        "location":float(dic["location"]),
                        "regul":dic["regul"],
                        "net":dic["net"],
                        "reporthost":dic["reporthost"],
                        "tab_requests":[
                            {
                                "date":nowDate,
                                "statuts":dic["status"],
                                "piscine":dic["piscine"] 
                            }]
                        })


#%%%%%%%%%%%%%  main driver function
if __name__ == '__main__':
    
    # run() method of Flask class runs the application 
    # on the local development server.
    app.run(debug=False) #host='127.0.0.1', port=5000)
    

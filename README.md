Projet IoT de gestion des piscines : WaterBnB_22016588
=================

## Table des Matières

1. [Introduction](#introduction)
2. [Contributeurs](#contributeurs)
3. [Utiles](#utiles)
4. [Technologies Utilisées](#technologies-utilisées)
5. [Documentation utilisateur](#documentation-utilisateur)
6. [Base de données mongo](#base-de-données-mongo)
7. [Autres](#autres)


## Introduction
Lors de notre master MIAGE, DIOP Serigne Rawane et BORREANI Théo avons réalisé un projet dans le cadre du cours "IoT & réseaux" de M. MENEZ Gilles. Le projet consiste en la réalisation d'un régulateur de température connecté avec un ESP32 et les langages C et Python pour la gestion de piscines.


## Contributeurs 
* DIOP Serigne Rawane
* BORREANI Théo


## Utiles

Pour consulter ou avoir le lien de notre application Python Flask, consultez le [WaterBnB_22016588](https://waterbnb-22016588.onrender.com).    

Pour consulter notre dashbord fait sur mongoDB Altas qui présente et analyse les informations importantes, veuillez cliquer sur ce lien pour y accéder [Dashbord MongoDB Altas WaterBnB_22016588](https://charts.mongodb.com/charts-project-0-ydbwe/public/dashboards/6617884f-a19d-46e5-8bf8-bc0847717734).  


## Technologies Utilisées

### Logiciels
* Arduino IDE 1.8.19
* C
* Python 3
* GitHub
* Node-RED
* HTML
* CSS 
* cURL

### Matériels 
* Une carte ESP32
* Des LEDs de couleurs
* Capteur de lumière
* Des résistances
* Un ventilateur
* Un thermomètre

## Documentation utilisateur

### Utilisation 

#### Arduino
1. Brancher l'ESP32 en respectant les broches.
1. Télécharger les bibliothèques nécessaires :
    * OneWire.h
    * DallasTemperature.h
    * Adafruit_NeoPixel.h
    * ArduinoJson.h
    * WiFi.h
    * WiFiMulti.h
    * SPIFFS.h
    * FS.h
    * ESPAsyncWebServer.h
    * ArduinoOTA.h
    * HTTPClient.h
1. Dans le code C principal **regul.ino**, une structure appelée Parametre est disponible. Vous pouvez modifier les variables et constantes, __notament target_ip et target_port avec votre adresse IP local et le port sur lequel est lancé Node-RED__.
1. Dans le menu outil, téleverser les fichiers grâce à __ESP32 Sketch Data Upload__.
1. Téléverser le code sur l'ESP32 depuis l'IDE Arduino.
1. (Optionnel) Si vous rencontrez une erreur de compilation, recommencez en changeant la variable de préprocesseur "__Old__" à 1 ou à 0.

#### Validateur dans le dossier **validator**
1. Modifier le fichier exemple_1.json à votre guise
1. Executer val.py avec python3
```
python3 val.py
```

#### Tableau de bord dans le dossier **node-red**
Cette interface sur le map est conçue pour gérer les locations et les positions des clients sur le map, offrant une visualisation géographique pour une meilleure gestion des emplacements et des services proposés. Elle nécessite une connexion client via un identifiant étudiant : **user**.

#### Script bash 

Un script shell est disponible pour tester les routes du serveur hébergés sur l'ESP32 via des commandes curl, vous pouvez modifier la variable ip avec l'IP qu'affichera votre ESP32 après la connexion.


## Base de données mongo

### Présentation de la structuration de la collection piscines
Nous avons décidé de structurer cette collection avec une liste d'objets représentant les ESP. Cette liste a donc autant d'éléments que d'ESP, à condition qu'elle passe le validateur JSON. Chaque élément contient des champs basiques (objet et type primitif) ainsi que des tableaux permettant, pour tab_requests, d'avoir un historique afin de visualiser, par exemple, l'évolution de la température d'une ESP en fonction du temps. Pour tab_demandes, cela permet d'avoir un historique de chaque demande.

### Présentation de la structuration de la collection users
Contient une liste des utilisateurs comprenant un nom, un id et un numéro étudiant.


## Autres

### Protection du serveur et de la base de données
Pour protéger notre serveur et notre base de données, nous avons utilisé un validateur JSON strict qui n'accepte que les JSON ayant une structure précise. Certains champs de type disposent notamment de valeurs énumérées possibles. De cette manière, nous espérons garantir que le serveur ne plantera pas et que la base de données restera uniforme, évitant ainsi tout problème lors de son utilisation par notre serveur. Nous avons aussi laissé tourné le serveur de nombreuses heures pour tester ca robustesse avec les différentes données que nous et nos camarades envoyé sur le broker.

<span style="color:#FFD700">
Par exemple, nous avons remarqué qu'il existe un champ sur le JSON "uptime", selon nous qui devrait être en numérique et que vous l'aviez mis en String sur les consignes donc nous l'avons gardé en String et que toutes les personnes qui l'ont mis en numérique ne vont pas passer notre validator.
</span>

### Les plus apporté
* Aucun délai n'est utilisé dans le code C. Au lieu de cela, nous utilisons des conditions et des variables qui nous permettent d'appeler des fonctions en choisissant indépendamment l'intervalle associé à chacune d'elles.
* Une carte intéractive disponible pour consulter la position théorique de l'ESP32.
* Une grande variété d'indicateurs.

<span style="color:#FFD700">
MERCI ET BONNE LECTURE !
</span>




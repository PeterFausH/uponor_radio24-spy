# -*- coding: utf-8 -*-
# erstellt: Peter Fürle
# fragt am Uponor @home die Temperaturen und Zustände ab
# Mozilla Addon LiveHTTPheaders genutzt zum Mitschneiden
#Info
#Temperatur über Weboberfläche setzen, entweder Wunschtemp oder 255 für Raumthermostatvorgabe
#data = {"jsonrpc":"2.0","id":125,"method":"write","params":{"objects":[{"id":"2564","properties":{"85":{"value":255}}}]}}
#Sniffer:
#POST /api {"jsonrpc":"2.0","id":39,"method":"read","params":{"objects":[{"id":"12","properties":{"85":{}}},{"id":"407","properties":{"85":{}}},{"id":"2232","properties":{"85":{}}},{"id":"2235","properties":{"85":{}}},{"id":"2511","properties":{"85":{}}}]}}

import requests
import json
from influxdb import InfluxDBClient


#lines für line-protocol influx
p = ""

# Configure InfluxDB connection variables
host = "127.0.0.1" 
port = 8086 
user = "uponor"
password = "home"
dbname = "uponor" 


# Influx Datenbank verbinden
#influx
#> create database uponor
#> use uponor
#> create user uponor with password 'home' with all privileges
#> grant all privileges on uponor to uponor
client = InfluxDBClient(host, port, user, password, dbname)

alarm = ''
an = []

#arrays anlegen mit meinen Raumbezeichnungen
#          0        1           2               3          4          5               6             7                 8           9              10            11         12    
Raum_T = ["UG-Gaestebad","UG-Wohnzimmer","UG-Stiefelraum","UG-Gaestekammer","UG-Diele","EG-Wohnzimmer","EG-Ankleide","EG-Schlafzimmer","EG-Kueche","EG-Elternbad","DG-Seeblick","DG-Diele","DG-Wellness"]
#Wattzahlen der einzelnen Räume FBH
Raum_W = [763,1287,321,581,732,2075,225,953,881,861,774,327,1011]
#Fläche der einzelnen Räume FBH
Raum_M = [5.5,21.5,5.4,9.7,10.8,25.6,3.2,15.9,14.7,6.5,12.9,5.5,7.5]
#diese Raumnummern aus der Weboberfläche heraus mitgeschnitten, Reihenfolge wie Räume
Raum_N = [139,149,159,169,179,19,29,39,49,59,259,269,279]
#Parameter der die Web-Soll-Temperatur angibt. Value=255 übergibt wieder an Thermostat
Raum_S = [2538,2540,2542,2544,2546,2512,2514,2516,2518,2520,2560,2562,2564]



#Datensatz für InfluxDB zusammenbauen
def add(i,name,wert):
    # Sonderfall für Allgemein-Info die nicht Raumabhängig sind.
    if i==99:
        info=[
        {
            "measurement": "uponor",
                "tags": {
                    "bereich": "KM4_Allgemein"
                },
            "fields": {
                name : wert
            }
        }
        ]
        
    else:
        info=[
        {
            "measurement": "uponor",
                "tags": {
                    "bereich": "KM4_"+Raum_T[i]
                },
            "fields": {
                name : wert
            }
        }
        ]
    #print(info)
    client.write_points(info, time_precision='m')
    return

#Raum_N = Aktuelle Temperatur
#Raum_N + 1 = Soll Temperatur am Thermostat
#Raum_N + 4 = Heizen 0/1

#Alle Räume bearbeiten
i = 0
leistung = 0
flaeche = 0
while i < 13:
    #Abfrage-String zusammenbasteln
    data = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "read",
        "params": {
            "objects": [
                {
                    "id": "1",
                    "properties": {
                        "85": {}
                    }
                },
                {
                    "id": Raum_N[i],
                    "properties": {
                        "85": {}
                    }
                },
                {
                    "id": Raum_N[i]+1,
                    "properties": {
                        "85": {}
                    }
                },
                {
                    "id": Raum_N[i]+3,
                    "properties": {
                        "85": {}
                    }
                },
                {
                    "id": Raum_N[i]+4,
                    "properties": {
                        "85": {}
                    }
                },
                {
                    "id": Raum_N[i]+5,
                    "properties": {
                        "85": {}
                    }
                },
                {
                    "id": Raum_S[i],
                    "properties": {
                        "85": {}
                    }
                },
                {
                    "id": Raum_N[i]+7,
                    "properties": {
                        "85": {}
                    }
                }
            ]
        }
    }
    #diesen Header beim Request mitschicken
    headers = {'content-type': 'application/json', 'charset': 'utf-8'}
    #mein Uponor @home Gerät
    url = 'http://192.168.22.206:80/api'
    #Uponor @home abfragen
    r = requests.post(url, data=json.dumps(data), headers=headers)
    json_string = json.dumps(r.json())
    parsed_json = json.loads(json_string)
    #Json auswerten
    status=["Nein","-Ja-"]
    akt_temp = (parsed_json["result"]["objects"][1]["properties"]["85"]["value"])
    soll_temp = (parsed_json["result"]["objects"][2]["properties"]["85"]["value"])
    plus3 = (parsed_json["result"]["objects"][3]["properties"]["85"]["value"])
    heizt = int((parsed_json["result"]["objects"][4]["properties"]["85"]["value"]))
    webisttemp = int((parsed_json["result"]["objects"][5]["properties"]["85"]["value"]))
    web_soll = (parsed_json["result"]["objects"][6]["properties"]["85"]["value"])
    plus7 = (parsed_json["result"]["objects"][7]["properties"]["85"]["value"])


    #Bildschirmausgabe Flächenberechnung
    if status[heizt] == "-Ja-":
        #print ("%17r IST: %4.1f, SOLL: %4.1f, Heizt: %s, Watt: %6.1f, Flaeche: %5.1f, plus3: %5.1f, plus7: %5.1f"  % (Raum_T[i], akt_temp, soll_temp, status[heizt],Raum_W[i],Raum_M[i],plus3,plus7))
        leistung = leistung + Raum_W[i]
        flaeche = flaeche + Raum_M[i]
        #erzeugt eine Liste ob FBH im Raum an oder aus ist
        #hier wird an die Liste _w für Warm angehängt. 
        an.append("_w")
    else:
##        print ("%17r IST: %4.1f, SOLL: %4.1f, Heizt: %s, plus3: %5.1f, plus7: %5.1f"  % (Raum_T[i], akt_temp, soll_temp, status[heizt],plus3,plus7))
        an.append("_k")

    #influx-Datenbank
    add(i,"Solltemp",soll_temp)
    add(i,"Isttemp",akt_temp)
    add(i,"Heizt",heizt)
    add(i,"HTML",webisttemp)
    add(i,"HTML-Soll-Temp",web_soll)
    i = i+1


# Allgemeindaten anfügen    
add(99,"Heizleistung",leistung)
add(99,"Heizfläche",flaeche)


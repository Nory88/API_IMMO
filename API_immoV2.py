from flask import Flask, request, jsonify
import googlemaps

app = Flask(__name__)

"""
######################################################################################################################## 
              FONCTION CODEPOSTALE DETERMINE LE CODE POSTAL A PARTIR DE LA LATITUDE ET LONGITUDE
########################################################################################################################
"""
gmaps = googlemaps.Client(key='METS TA CLEF ICI')

def codepostale(latitude, longitude):
    # Look up an address with reverse geocoding
    reverse_geocode_result = gmaps.reverse_geocode((latitude, longitude), result_type='postal_code')
    return reverse_geocode_result[0]['address_components'][0]['long_name']

"""
######################################################################################################################## 
CI-DESSOUS MODELES MULTILINEAIRES SELON ARRONDISSEMENT. 
parfois le modèle global (ie prenant l'ensemble des valeurs lyonnaises) était plus précis que le modèle entrainé sur
l'arrondssement en question...
En amont, tri des valeurs de la manière suivante:
- nous avons grader les appartements uniquement
- une valeur foncière compris entre 55K et 1m d'€
- surface réelle bâtie comprise entre 10  et 200
- coût au mètre carré de maximum 10k€
- suppression des valeurs nulles.
########################################################################################################################
"""

def multilinearregressionpararrondissement(code, pieces, surface):
    if code=='69001': #Variance score: 0.78
        return pieces*(10588.086253934542)+surface*(3385.3793674843523)
    elif code=='69002':#Variance score: 0.65
        return pieces*(16386.614565894186)+surface*(4010.873460399845)
    elif code=='69003': #Variance score: 0.75
        return pieces*(3706.6228578209852)+surface*(3731.802917414372)
    elif code=='69004':#Variance score:0.46 (interch global:0.76)
        return pieces*(97.27471085509451)+surface*(3926.5396558064126)
    elif code=='69005':#Variance score: 0.74
        return pieces*(-7070.484609256459)+surface*(3811.0865012302493)
    elif code=='69006':#Variance score: 0.75
        return pieces*(28039.491269644757)+surface*(3337.6611277894553)
    elif code=='69007':#Variance score: 0.87
        return pieces*(-7947.071648157299)+surface*(3862.7734385717185)
    elif code=='69008':#Variance score:0.5 (interch global:0.76)
        return pieces*(97.27471085509451)+surface*(3926.5396558064126)
    elif code=='69009':#Variance score:0.60 (interch global:0.76)
        return pieces*(97.27471085509451)+surface*(3926.5396558064126)
    else:
        return "error"

@app.route('/APIPOST', methods=['POST'])
def fonction():
    #result=request.json['latitude']
    result=request.json['latitude']
    return jsonify({'ça fonctionne': result})

@app.route('/API', methods=['POST','GET'])
def API():
    error1={'result':'valeur(s) manquante(s) pour estimer votre bien!'}
    error2={'result':'bien hors périmètre lyonnais'}
    error3={'result':'coordonnées GPS impossible'}
    superficie=request.json['superficie']
    nb_pieces=request.json['nb_pieces']
    lat=request.json['latitude']
    lon=request.json['longitude']
    if superficie == None:
        return jsonify(error1)
    if nb_pieces == None:
        return jsonify(error1)
    if lat == None:
        return jsonify(error1)
    if lon == None:
        return jsonify(error1)
    if codepostale(lat,lon) == None:
        return
    if codepostale(lat , lon) not in ['69001' , '69002' , '69003' , '69004' , '69005' , '69006' , '69007' , '69008' , '69009']:
        return jsonify(error2)
    try:
        code=codepostale(lat,lon)
        result=multilinearregressionpararrondissement(code,nb_pieces,superficie)
        return jsonify({'result':result})
    except IndexError:
        return jsonify(error3)



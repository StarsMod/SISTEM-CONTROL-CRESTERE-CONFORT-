import pyrebase
import time
import board
import adafruit_dht
from gpiozero import PWMLED

def fixNota(nota):
    if(nota <= 1):
        nota = 1
    if(nota >= 5):
        nota = 5
    return nota

config = {
  "apiKey": "AIzaSyC5haWIDbb7vexyk9pdsVUn4A66CYsyUaQ",
  "authDomain": "licenta-4884e.firebaseapp.com",
  "databaseURL": "https://licenta-4884e-default-rtdb.firebaseio.com",
  "projectId": "licenta-4884e",
  "storageBucket": "licenta-4884e.appspot.com",
  "messagingSenderId": "762055110552",
  "appId": "1:762055110552:web:9cedbeac9b9cbd11f685ed",
  "measurementId": "G-6KW0J968FB"
};




firebase = pyrebase.initialize_app(config)
database = firebase.database()

sensor = adafruit_dht.DHT22(board.D4, use_pulseio=False)
lumina = PWMLED(17)

note = database.child("note").get().val()
ultimaNota = note[next(reversed(note))]

notaLumina = fixNota(ultimaNota['notaLumi'])
notaTemperatura = fixNota(ultimaNota['notaTemp'])
notaUmiditate = fixNota(ultimaNota['notaUmid'])

setpoints = database.child("setpoint").get().val()

setpointLumina = setpoints["setpointLumi"]
setpointTemperatura = setpoints["setpointTemp"]
setpointUmiditate = setpoints["setpointUmid"]

limitaTemperatura = 1
limitaUmiditate = 10

incalzire = False
racire = False
umidificare = False
dezumidificare = False

try:
    temperaturaCitita = sensor.temperature
    umiditateCitita = sensor.humidity
except RuntimeError as error:
    print(error.args[0])
except Exception as error:
    sensor.exit()

#diferentaLumina = setpointLumina - 50
diferentaTemperatura = setpointTemperatura - temperaturaCitita
diferentaUmiditate = setpointUmiditate - umiditateCitita


if (diferentaTemperatura > 0):
    targetTemperatura = temperaturaCitita + limitaTemperatura*(1+(1-notaTemperatura)*0.25)
elif (diferentaTemperatura < 0):
    targetTemperatura = temperaturaCitita - limitaTemperatura*(1+(1-notaTemperatura)*0.25)
else :
    targetTemperatura = setpointTemperatura - limitaTemperatura

if (diferentaUmiditate > 0):
    targetUmiditate = umiditateCitita + limitaUmiditate*(1+(1-notaUmiditate)*0.25)
elif (diferentaTemperatura < 0):
    targetUmiditate = umiditateCitita - limitaUmiditate*(1+(1-notaUmiditate)*0.25)
else :
    targetUmiditate = setpointUmiditate - limitaUmiditate

targetLumina = -1*(-50 + (notaLumina - 1) * 25) + setpointLumina
#targetTemperatura = -1*(-1 + (notaTemperatura - 1) * 0.5) + setpointTemperatura
#targetUmiditate = -1*(-10 + (notaUmiditate - 1) * 5) + setpointUmiditate

if (targetLumina > 100):
    targetLumina = 1
if (targetLumina < 0):
    targetLumina = 0
else : 
    targetLumina = targetLumina / 100

lumina.value = targetLumina

if (targetTemperatura > temperaturaCitita):
    
    incalzire = True
    racire = False
    
elif (targetTemperatura < temperaturaCitita - 0.5):
    
    incalzire = False
    racire = True
    
if (targetUmiditate > umiditateCitita):
    
    umidificare = True
    dezumidificare = False
    
elif (targetUmiditate < umiditateCitita - 3):
    
    umidificare = False
    dezumidificare = True

print(f'''Nota Lumina: {notaLumina} -> setpoint: {setpointLumina}
TARGET DE {targetLumina*100}% \n
Nota Temperatura: {notaTemperatura} -> setpoint: {setpointTemperatura}
TARGET DE {targetTemperatura} Temperatura curenta: {temperaturaCitita} \n
Nota Umiditate: {notaUmiditate} -> setpoint: {setpointUmiditate}
TARGET DE {targetUmiditate} Umiditate curenta: {umiditateCitita}\n
Incalzire : {incalzire} // Racire : {racire} \n
Umidificare : {umidificare} // Dezumidificare : {dezumidificare}''')

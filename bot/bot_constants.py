import secrets

pass_key = secrets.pass_key_bicimad
client_id = '2b6eac54-0f6c-4897-a79c-23e9b64fed8a'
stations_id = [1538, 1611, 1645, 1610, 2362]
custom_station_names = {
    1538: 'Cuatro Caminos (la de abajo)',
    1645: 'Francos Rodriguez (la que esta arriba)',
    1611: 'Estrecho (la que está aquí al lado)',
    1610: 'Cuatro Caminos (la de Orange)',
    2362: 'tu calle, al fondo fondo (izquierda)'
    }

coordinates = {
    'longitude': '-3.706',
    'latitude': '40.4516',
    'radius': '600'
}

message = {
    'single': 'En la estación de {}; hay {} bicis dispobibles.'
}
WEATHER_API_KEY = '020c34777ba593331d1bab78e24e44a2'



URL_WEATHER = "http://api.openweathermap.org/data/2.5/weather?"
SERVER_URL = "http://192.168.1.123"
# Telegram constants
GROUP_CHAT_ID = '-1001763995292'
DEVELOPER_CHAT_ID = '63210791'
ALLOWED_IDS = [DEVELOPER_CHAT_ID, GROUP_CHAT_ID]
BUTTONS_PRICE = ['Precio ahora', 'Gráfica del día']
IMAGE_FOLDER = 'bot_images/'

# Data constants
data_prefix = 'data/'
SUBTRACTS_FILE = data_prefix + 'subtracts.json'
PANEOS_FILE = data_prefix + 'paneos.json'
DEVICES_FILE = data_prefix + 'devices.json'

ANDREA_PHRASES = [
    "Andrea trancuila respira",
    'Andreeeea cchiiill reláaajate 😇😚',
    "Inspirar, expirar, inspirar, expirar",
    "😌🙌🏼🪷🌾",
    "Piensa en un gatito 🐈",
    "Hacemos Yoooooga?",
    "Vamos al parque a hacer ESTAF. O a bailar ;)"
]
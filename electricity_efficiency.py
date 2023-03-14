from aiopvpc.pvpc_data import asyncio, datetime
import tinytuya
from aiopvpc import PVPCData
import aiohttp
import requests
from heapq import nlargest, nsmallest
import json
import time
import asyncio
# ID: adgvrfkwhc5ap44djnd4
# Secret: 3a03cc82d0154e91bca4111f241395c4
# Project code: p1678452019575ty5dj5
WEATHER_API_KEY = '020c34777ba593331d1bab78e24e44a2'
URL_WEATHER = "http://api.openweathermap.org/data/2.5/weather?"
DEVICES_PATH ='data/devices.json'
with open(DEVICES_PATH, 'r') as d:
    devices = json.load(d)
    
def calculate_weather(WEATHER_API_KEY, URL_WEATHER):
    complete_url = URL_WEATHER + "appid=" + WEATHER_API_KEY + "&q=" + 'Peña Grande'
    response = requests.get(complete_url)
    x = response.json()
    if x["cod"] != "404":
        y = x["main"]
        temp = y["temp"] - 273.15
        humidity = y["humidity"]
        z = x["weather"][0]['description']
        return temp, humidity

def load_device(device_name: str) -> tinytuya.OutletDevice:
    device_data = [i for i in devices if device_name in i['name'].lower()][0]
    device_ID = device_data['id']
    device_IP = device_data['ip']
    device = tinytuya.OutletDevice(device_ID, device_IP, None,
                                        version=3.3, dev_type='default')
    return device
async def get_prices():  
    async with aiohttp.ClientSession() as session:
        pvpc_handler = PVPCData(session = session, tariff = "2.0TD")
        prices: dict = await pvpc_handler.async_update_all(current_data=None, now=datetime.now())
        prices=prices.sensors['PVPC']
        prices = {k.hour: v for k, v in prices.items()}
    return prices

async def get_price_now():
    prices = await asyncio.create_task(get_prices())
    price_now = prices[datetime.now().hour]
    text=f'Precio de la electricité ahora es {price_now} €/kWh.'
    if price_now > min(nlargest(8, prices.values())):
        text+=' Esto es algo caro! 💸💴'
    elif price_now < max(nsmallest(8, prices.values())):
        text+=' Aprovecha ahora para cosas tochas y ahorrar 🤑'
    else:
        text+=' Esto es normalito 🥹'

async def main():
    t, _ = calculate_weather(WEATHER_API_KEY, URL_WEATHER)
    # prices = await asyncio.create_task(get_prices())
    
    prices = get_prices()
    lowest_prices = nsmallest(6, prices.values())
    lowest_prices = nlargest(6, prices.values())
    
    device = load_device('calentador')
    data = device.status() 
    print('Device status: %r' % data)
    device.turn_on()
    device.turn_off()
    time.sleep(2.4)
    
if __name__ == "__main__":
    main()
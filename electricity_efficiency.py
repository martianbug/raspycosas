# Example Usage of TinyTuya
from aiopvpc.pvpc_data import asyncio, datetime
import tinytuya
from aiopvpc import PVPCData
import aiohttp

# ID: adgvrfkwhc5ap44djnd4
# Secret: 3a03cc82d0154e91bca4111f241395c4
# Project code: p1678452019575ty5dj5
from heapq import nlargest, nsmallest
import json

with open('devices.json', 'r') as d:
    devices = json.load(d)
def load_device(device_name: str) -> tinytuya.OutletDevice:
    device_data = [i for i in devices if device_name in i['name'].lower()][0]
    device_ID = device_data['id']
    device_IP = device_data['ip']
    # device_KEY = device_data['key']
    device = tinytuya.OutletDevice(device_ID, device_IP, None,
                                        version=3.3, dev_type='default')
    return device
async def get_price():  
    async with aiohttp.ClientSession() as session:
        pvpc_handler = PVPCData(session = session, tariff = "2.0TD")
        prices: dict = await pvpc_handler.async_update_all(current_data=None, now=datetime.now())
        prices=prices.sensors['PVPC']
        prices = {k.hour: v for k, v in prices.items()}
    return prices

prices = await asyncio.create_task(get_price())
price_now = prices[datetime.now().hour]
text=f'Precio de la electricité ahora es {price_now} €/kWh.'
if price_now > min(nlargest(8, prices.values())):
    text+=' Esto es algo caro! 💸💴'
elif price_now < max(nsmallest(8, prices.values())):
    text+=' Aprovecha ahora para cosas tochas y ahorrar 🤑'
else:
        text+=' Esto es normalito 🥹'

device = load_device('calentador')
data = calentador.status() 
print('Device status: %r' % data)
calentador.turn_on()
calentador.turn_off()
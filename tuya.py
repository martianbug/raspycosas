# Example Usage of TinyTuya
import tinytuya

# ID: adgvrfkwhc5ap44djnd4
# Secret: 3a03cc82d0154e91bca4111f241395c4
# Project code: p1678452019575ty5dj5
import json

with open('devices.json', 'r') as d:
    devices = json.load(d)
    
calentador_data = [i for i in devices if 'Calentador' in i['name']][0]
calentador_ID = calentador_data['id']
calentador_IP = calentador_data['ip']
calentador_KEY = calentador_data['key']
calentador = tinytuya.OutletDevice(calentador_ID, calentador_IP, None,
                                   version=3.3, dev_type='default')
# cloud = tinytuya.Cloud(
data = calentador.status() 
print('Device status: %r' % data)
calentador.turn_on()
calentador.turn_off()
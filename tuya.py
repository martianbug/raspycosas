# Example Usage of TinyTuya
import tinytuya

# ID: adgvrfkwhc5ap44djnd4
# Secret: 3a03cc82d0154e91bca4111f241395c4
# Project code: p1678452019575ty5dj5
import json

with open('data/devices.json', 'r') as d:
    devices = json.load(d)
    
calentador_data = [i for i in devices if 'Calentador' in i['name']][0]
d_ID = calentador_data['id']
d_IP = calentador_data['ip']
d_KEY = calentador_data['key']
d = tinytuya.OutletDevice(d_ID, 'device22',
                                   version=3.3, dev_type='default')
d.set_dpsUsed({"1": None}) 
data = d.status() 
print('Device status: %r' % data)
# cloud = tinytuya.Cloud(
d.turn_on()
d.turn_off()
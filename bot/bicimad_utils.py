'''
This file handles the login and extraction of values for some specific stations
'''
from stations import station_names
import requests
from collections import defaultdict
import bot_constants as C

url_login = 'https://openapi.emtmadrid.es/v1/mobilitylabs/user/login/'
url_station_info = 'https://openapi.emtmadrid.es/v1/transport/bicimad/stations/{}'
url_station_around = 'https://openapi.emtmadrid.es/v1/transport/bicimad/stations/arroundxy/{longitude}/{latitude}/{radius}/'

def login():
    headers = {
        'X-ClientId': C.client_id,
        'passKey': C.pass_key
    }
    r = requests.get(url_login, headers=headers)
    return(r.json()['data'][0]['accessToken'])

def get_station_info(access_token, station_id = ''):
    if not access_token:
        print('Missing parameter: accessToken')
        exit(1)
    if not station_id:
        print('Missing parameter: station_id')
        exit(1)
    
    url_station_info_updated = url_station_info.format(station_id)
    headers = {
        'accessToken': access_token
    }
    r = requests.get(url_station_info_updated, headers=headers)
    return(r.json()['data'][0])

def login_and_get_vals(coordinates = None):
    '''
    It returns a dictionary where the key is the number of available bikes. 
    That will help to sort the stations by available bikes
    '''
    station_ids = C.stations_id
    access_token = login()
    results = defaultdict()
    if coordinates:
        for radius in ('100', '200', '500', '600'):
            coordinates['radius'] = radius
            results_coords = get_info_from_cords(access_token, coordinates)
            if len(results_coords) > 4:
                break
        for res in results_coords:
            results[res['id']] = [res['dock_bikes'], res['geometry']['coordinates']]
    else:
        for station_id in station_ids:
            result_station_json = get_station_info(access_token, station_id)
            results[result_station_json['dock_bikes']].append(station_id)
    return(results)

def print_results_casa(results: dict):
    full_message = ''
    sorted_results = sorted(results.items(), key=lambda x:x[1], reverse=True)
    for result in sorted_results:
        station_id = result[0]
        available_bikes = result[1][0]
        station_name = station_names[station_id]['name'].split(' - ')[-1] if station_id not in C.custom_station_names.keys() else C.custom_station_names[station_id]
        single_message = C.message['single'].format(station_name, available_bikes)
        full_message += single_message + '\n'
    return(full_message)

def print_results(results: dict):
    full_message = ''
    for station_id in results.keys():
        bikes = results[station_id][0]
        coords = results[station_id][1]
        full_message += format_station_name(bikes, station_id, coords)
    return(full_message)

def format_station_name(available_bikes, station_id, coordinates):
    # url = f'google.com/maps/place/{coordinates[1]},{coordinates[0]}'
    url = f'https://maps.google.com?q={coordinates[1]},{coordinates[0]}'
    station_name = station_names[station_id]['name'].split(' - ')[-1] if station_id not in C.custom_station_names.keys() else C.custom_station_names[station_id]
    single_message = C.message['single'].format(f'<a href="{url}">{station_name}</a>', available_bikes)
    return single_message + '\n'

def get_info_from_cords(access_token, coordinates):
    if not access_token:
        print('Missing parameter: accessToken')
        exit(1)
    url_station_around_updated = url_station_around.format(
        longitude = coordinates['longitude'],
        latitude = coordinates['latitude'],
        radius = coordinates['radius'],
        )
    headers = {
        'accessToken': access_token
    }
    r = requests.get(url_station_around_updated, headers=headers)
    return(r.json()['data'])

def process_info_from_nearby(results_json):
    '''
    This is to be used with get_info_from_cords
    '''
    final_results = defaultdict(list)
    for station in results_json:
        final_results[station['id']].append(station['dock_bikes'])
    return(final_results)


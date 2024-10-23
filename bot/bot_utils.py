import asyncio
import csv
import difflib
import html
import json
import csv
import logging
import os
import random
import shutil
import time
import traceback
from datetime import datetime
from heapq import nlargest, nsmallest
import aiohttp
import bot_constants as C
import matplotlib.pyplot as plt
import my_secrets
import numpy as np
import requests
from aiopvpc import PVPCData
from bicimad_utils import login_and_get_vals, print_results, print_results_casa
from gtts import gTTS
from joblib import Parallel, delayed
from scipy.interpolate import interp1d
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler
from translate import Translator
from requests import post

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
DEL_ITEM = range(1)

translator_italian = Translator(from_lang = 'es', to_lang="it", pro = True)


def text_to_speech(text):
    speech = gTTS(text, lang='it')
    speech_file = 'speech.mp3'
    speech.save(speech_file)
    return speech_file
    
def read_csv_as_list(file_path):
    with open(file_path, 'r') as csvfile:
        data = list(csv.reader(csvfile))[0]
    return data

def save_list_as_csv(data, file_path):
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter = ',')
        writer.writerow(data)
           
def check_permission(update: object):
    if str(update.effective_chat.id) not in C.ALLOWED_IDS:
        return False
    return True

async def chill(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    frase = random.choice(C.ANDREA_PHRASES)
    await update.message.reply_text(frase)
    
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    # Build the message with some markup and additional information about what happened.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )
    await context.bot.send_message(
        chat_id=C.DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
    )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Lo siento, ese comando no lo conozco")
    
async def sad(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    os.system('mpg123 ' + 'data/sounds/sad.mp3')
    

async def speech(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    if len(context.args)<1:
        await update.message.reply_text(f'Pero qué digo???')
        return
    msg = ' '.join(context.args)
    speech_file = text_to_speech(msg)
    os.system('mpg123 ' + speech_file)
    os.system('rm '+ speech_file)
    
async def speech_italian(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    if len(context.args)<1:
        await update.message.reply_text(f'Pero qué digo???')
        return
    msg = ' '.join(context.args)
    msg_translated = translator_italian.translate(msg)
    speech_file = text_to_speech(msg_translated)
    os.system('mpg123 ' + speech_file)
    os.system('rm '+ speech_file)


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_keyboard = [[C.BUTTONS_PRICE[0], C.BUTTONS_PRICE[1]]]
    await update.message.reply_text(
        "Elije una opción:",
        reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder=""
            ),
        )
    
async def switch_sound(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if os.popen("pactl list short modules | grep module-loopback | wc -l").read()[0]>='1':
            os.system("pactl unload-module module-loopback")
            await update.message.reply_text(f'Sonido Chromecast offf')
        else:
            os.system("pactl load-module module-loopback")
            await update.message.reply_text(f'Sonido Chromecast onnn')

async def set_volumen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 1 or len(context.args[0])>3:
        await update.message.reply_text(f'Debes decirme un número de volumen')
        return
    v = int(context.args[0])
    await update.message.reply_text(f'Volumen al {v}%')
    os.system(f"pulsemixer --set-volume {v}")

# async def spotify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
#     os.system('sh ./attach_spotify.sh')
#     await update.message.reply_text(f'Music ON')
    
# async def spotify_stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
#     os.system(' ./spotify_stop.sh')
#     await update.message.reply_text(f'Music OFF')
    
async def increase_volume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            await update.message.reply_text(f'Subiendo volumen')
            os.system("pulsemixer --change-volume +10")    

async def decrease_volume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            await update.message.reply_text(f'Bajando volumen')
            os.system("pulsemixer --change-volume -10")            


async def proyector_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if check_permission(update):
        if shutil.which('irsend') is None:
            context.error = Exception('Bot operando en terminal Windows. No es posible encederlo')
            await update.message.reply_text(f'No se puede encender proyector ahora.')
            await asyncio.create_task(error_handler(update, context))
        else:
            await update.message.reply_text(f'Encendiendo proyector!')
            os.system("irsend SEND_ONCE BENQ_W1070 KEY_POWER")
    else:
        await update.message.reply_text(f'No tienes permiso para emitir esa orden!')

async def proyector_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if check_permission(update):
        await update.message.reply_text(f'Apagando proyector. Boas noites.')
        os.system("irsend SEND_START BENQ_W1070 KEY_POWER")
        time.sleep(0.5) 
        os.system("irsend SEND_STOP BENQ_W1070 KEY_POWER")
        os.system("irsend SEND_ONCE BENQ_W1070 KEY_POWER")
    else:
        await update.message.reply_text(f'No tienes permiso para emitir esa orden!')

'''
[BEGIN] SHOPPING LIST SECTION
'''
async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = []
    if len(context.args) < 1:
        await update.message.reply_text(f'Debes decirme algo para comprar')
        return
    if not os.path.exists(C.ITEMS_FILE):
        save_list_as_csv([], C.ITEMS_FILE)
    with open(C.ITEMS_FILE,'r+') as f:
        if os.path.getsize(C.ITEMS_FILE) == 0:
           data = []
        else:
            data = read_csv_as_list(C.ITEMS_FILE)
    items = ' '.join(context.args[0:]).strip().split('-')
    with open(C.ITEMS_FILE, "w") as f:
        for item in items:
            await add_item_to_file(update, data, item)

async def add_item_to_file(update, data, item):
    if item:
        item = item.strip()
        if item not in set(data):
            data.append(item)        
            save_list_as_csv(data, C.ITEMS_FILE)
        else:
            await update.message.reply_text(f'{item} ya estaba en la lista!')   
        await update.message.reply_text(f'"{item}" añadido ;)')

async def delete_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 1:
        await update.message.reply_text(f'Debes decirme algo que eliminar!')
        return
    item = ' '.join(context.args[0:]).strip()
    data = read_csv_as_list(C.ITEMS_FILE)
    if item not in data:
        try:
            closest = difflib.get_close_matches(item, data)[0]
            data.remove(closest)
            await update.message.reply_text(f'Has escrito "{item}" regulín pero lo he encontrado! "{closest}" eliminado ;)')        
        except:
            await update.message.reply_text(f'"{item}" no está en la lista!')        
            return
    else:
        data.remove(item)
        await update.message.reply_text(f'"{item}" eliminado ;)')
    save_list_as_csv(data, C.ITEMS_FILE)

async def reset_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    save_list_as_csv([], C.ITEMS_FILE)
    await update.message.reply_text('Lista booorrada :D')
    
def reset_file(file: str) -> None:
    data = {}
    with open(file,'w') as f:
        if not os.path.getsize(file) == 0:
            f.write(json.dumps(data))
            
def consult_file_items(file: str) -> None:
    if not os.path.exists(file) or os.stat(file).st_size == 0:
        return []
    data = read_csv_as_list(C.ITEMS_FILE)
    return data
    
async def list_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    items = consult_file_items(C.ITEMS_FILE)
    if items:
        message =  "La lista de la compra actual es:\n• " + "\n• ".join(items)
    else:
        message = "Lista vacía"
    await update.message.reply_text(message)


async def cine_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Modo cine activado! 🎦')
    url = my_secrets.HOMEASSISTANT_URL + 'scene/turn_on'
    data = {"entity_id": 'scene.cine'}
    response = post(url, headers=my_secrets.HOMEASSISTANT_HEADERS, json=data)
    print(response.text)

async def full_light_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'LUZZ 💡')
    url = my_secrets.HOMEASSISTANT_URL + 'scene/turn_on'
    data = {"entity_id": 'scene.full_light'}
    response = post(url, headers=my_secrets.HOMEASSISTANT_HEADERS, json=data)
    print(response.text) 
     
async def mesa_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text(f'Luz mesa')
        url = my_secrets.HOMEASSISTANT_URL + 'scene/turn_on'
        data = {"entity_id": 'scene.luz_mesa'}
        response = post(url, headers=my_secrets.HOMEASSISTANT_HEADERS, json=data)
    except:
        await update.message.reply_text(f'Problemas con la conexion a Home Assistant!')

async def cozy_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        url = my_secrets.HOMEASSISTANT_URL + 'scene/turn_on'
        data = {"entity_id": 'scene.cozy'}
        response = post(url, headers=my_secrets.HOMEASSISTANT_HEADERS, json=data)
        await update.message.reply_text(f'Trrrranqui tiiio')
    except:
        await update.message.reply_text(f'Problemas con la conexion a Home Assistant!')
        
async def leds_studio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = my_secrets.HOMEASSISTANT_URL + 'light/toggle'
    data = {"entity_id": 'light.leds_studio_luz_2'}
    response = post(url, headers=my_secrets.HOMEASSISTANT_HEADERS, json=data)
    print(response.text)  

async def romantic_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'💖')
    url = my_secrets.HOMEASSISTANT_URL + 'scene/turn_on'
    data = {"entity_id": 'scene.romantic'}
    response = post(url, headers=my_secrets.HOMEASSISTANT_HEADERS, json=data)
    print(response.text)  
     
async def controller(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    items = ['/romantic', '/luz_mesa', '/luz', '/cine', '/cozy', '/leds_studio']
    reply_keyboard = [items + ['/salir']]
    await update.message.reply_text(
        "Qué enciendo?",
        reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard = False, input_field_placeholder="",
            resize_keyboard = True,
            ),
        )
    return 1

async def control_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END

async def delete_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    items = consult_file_items(C.ITEMS_FILE)
    if not items:
        message = "Lista vacía"
        await update.message.reply_text(message)
        return
    reply_keyboard = [items + ['/salir']]
    await update.message.reply_text(
        "Elije un item: ",
        reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard = False, input_field_placeholder="",
            resize_keyboard = True,
            
            ),
        )
    return DEL_ITEM

async def delete_markup_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    item = update.message.text
    data = read_csv_as_list(C.ITEMS_FILE)
    data.remove(item)
    await update.message.reply_text(f'"{item}" eliminado ;)')
    save_list_as_csv(data, C.ITEMS_FILE)
    # return ConversationHandler.END
    return DEL_ITEM
'''
[END] SHOPPING LIST SECTION
'''

'''
[BEGIN] ELECTRICITY PRICE SECTION
'''
async def get_price():  
    async with aiohttp.ClientSession() as session:
        pvpc_handler = PVPCData(session = session, tariff = "2.0TD")
        prices: dict = await pvpc_handler.async_update_all(current_data=None, now=datetime.now())
        prices = prices.sensors['PVPC']
        prices = {k.hour: v for k, v in prices.items()}
    return prices

async def get_price_now(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prices = await asyncio.create_task(get_price())
    price_now = prices[datetime.now().hour]
    text=f'Precio de la electricité ahora es {price_now} €/kWh.'
    if price_now > min(nlargest(8, prices.values())):
        text+=' Esto es algo caro! 💸💴'
    elif price_now < max(nsmallest(8, prices.values())):
        text+=' Aprovecha ahora para cosas tochas y ahorrar 🤑'
    else:
         text+=' Esto es normalito 🥹'
    await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    
def record_electricity_data(prices_json):
    final_row = [datetime.today().strftime('%d/%m/%Y')] + list(prices_json.values())
    with open(C.ELECTRICITY_FILE, 'w+') as data_file:
        csv_writer = csv.writer(data_file)
        csv_writer.writerow(final_row)
        data_file.close()

async def update_pvpc_graph():
    dest_path = os.path.join(C.IMAGE_FOLDER ,f'prices_{datetime.now().strftime("%d-%m-%Y %H_%M_%S")}.png')
    if os.path.exists(dest_path):
        return (dest_path, None)
    prices = await asyncio.create_task(get_price())
    record_electricity_data(prices)
    y = np.array(list(prices.values()))
    x = np.array(list(prices.keys()))
    cubic_interpolation_model = interp1d(x, y, kind = "cubic")
    X_ = np.linspace(x.min(), x.max(), 300)
    Y_ = cubic_interpolation_model(X_)
    plt.rcParams.update({'font.size': 22, 'font.family': 'sans-serif'})
    plt.figure(figsize=(16,10), dpi= 80)
    plt.grid()
    plt.title(f'Precios electricidad para el {datetime.now().strftime("%d-%m-%Y")}', fontsize=22)
    plt.ylabel("Precio en €/kWh")
    plt.xlabel("Hora")
    plt.locator_params(nbins=20, axis='x')
    # plt.legend(loc=2, prop={'size': 10})
    plt.plot(X_, Y_, 'g')
    plt.savefig(dest_path)
    return(dest_path, prices)

async def get_price_graph(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    electricity_graph, prices = await asyncio.create_task(update_pvpc_graph())
    await update.message.reply_photo(electricity_graph, reply_markup=ReplyKeyboardRemove())

async def electricity_alarms(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    hour = job.data['hour']
    kind = job.data['kind']
    message = ''
    if 'low' in kind:
        message = C.ELECTIRICY_SENTENCES_GOOD[random.randint(len(C.ELECTIRICY_SENTENCES_GOOD))].format(hour)
    else:
        message = C.ELECTIRICY_SENTENCES_BAD[random.randint(len(C.ELECTIRICY_SENTENCES_BAD))].format(hour)
    await context.bot.send_message(job.chat_id, text=message)

async def alarm_prices(context: ContextTypes.DEFAULT_TYPE) -> None:
    '''
    First, download today's data
    Second, extract max and min values from time periods. There are two period:
        - 8 - 17
        - 18 - 23
    Third, set the reminders to send a message around those times
    '''
    periods = {'morning': [8, 16],
                'evening': [17, 23]}
    sensibility = 2
    electricity_graph, prices = await asyncio.create_task(update_pvpc_graph())
    prices_sorted_by_time = dict(sorted(prices.items(), key=lambda item: item[0]))
    morning = list(prices_sorted_by_time.items())[periods['morning'][0]:periods['morning'][1]]
    evening = list(prices_sorted_by_time.items())[periods['evening'][0]:periods['evening'][1]]
    min_prices_morning = sorted(morning, key=lambda item: item[1])
    min_prices_evening = sorted(evening, key=lambda item: item[1])
    max_prices_morning = sorted(morning, key=lambda item: item[1], reverse=True)
    max_prices_evening = sorted(evening, key=lambda item: item[1], reverse=True)
    # Select the lowest prices and take the earliest from those
    #sensibility defines the range of times to select to get the highest and lowests
    values = {
        'lowest_early_morning_price': sorted(min_prices_morning[:sensibility])[0][0],
        'lowest_early_evening_price': sorted(min_prices_evening[:sensibility])[0][0],
        'highest_early_morning_price': sorted(max_prices_morning[:sensibility])[0][0],
        'highest_early_evening_price': sorted(max_prices_evening[:sensibility])[0][0]
    }
    for key in values.keys():
        context.job_queue.run_once(electricity_alarms, chat_id=C.GROUP_CHAT_ID, 
                                   when=time(hour = values[key]-1, minute = 50),
                                   data={'hour':values[key], 'kind': key})
        
async def set_job_peak_times(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #This functions runs every day at midnight to update the values of the day
    context.job_queue.run_daily(alarm_prices, chat_id=C.GROUP_CHAT_ID, time=datetime.time(0,1))

async def message_price_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if C.BUTTONS_PRICE[0] == update.message.text:
        await get_price_now(update, context)
    if C.BUTTONS_PRICE[1] == update.message.text:
        await get_price_graph(update, context)

'''
[END] ELECTRICITY PRICE SECTION
'''

'''
[BEGIN] WEATHER SECTION
'''
async def alarm_rain(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    complete_url = C.URL_WEATHER.format(mode=C.WEATHER) + "appid=" + C.WEATHER_API_KEY + "&q=" + 'Peña Grande'
    response = requests.get(complete_url)
    x = response.json()
    description = x["weather"][0]['description']
    if 'rain' in description.lower():
        await context.bot.send_message(job.chat_id, text=f"Llueve!!! 🌧️🌧️. Lo recordaré cada hora. Apaga con /alarma_lluvia_off")
        context.job.job.trigger.interval = 3000
        
async def set_job_rain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.job_queue.run_repeating(alarm_rain, chat_id=C.GROUP_CHAT_ID, interval=300, first=0)      
    await update.message.reply_text(f'Alarma antilluvia puesta!')

async def unset_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Alarma ancelada!" if job_removed else "No hay ninguna alarma ahora"
    await update.message.reply_text(text)

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    translator = Translator(from_lang = 'en', to_lang="es", pro = True)
    complete_url = C.URL_WEATHER.format(mode=C.WEATHER) + "appid=" + C.WEATHER_API_KEY + "&q=" + 'Peña Grande'
    response = requests.get(complete_url)
    x = response.json()
    if x["cod"] != "404":
        y = x["main"]
        temp = round(y["temp"] - 273.15, 2)
        temp_feel = round(y["feels_like"] - 273.15, 2)
        humidity = y["humidity"]
        description = x["weather"][0]['description']
        z_translated = translator.translate(description.capitalize())
    await update.message.reply_text(f"La temperatura es {temp}°C. Sensación termica: {temp_feel}°C.\nHumedad del {humidity}%. {z_translated}.")

async def weather_forecast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    translator= Translator(from_lang = 'en', to_lang="es", pro = True)
    complete_url = C.URL_WEATHER.format(mode=C.FORECAST) + "appid=" + C.WEATHER_API_KEY + "&q=" + 'Peña Grande'
    response = requests.get(complete_url)
    x = response.json()
    next_forecasts = x['list']
    if x["cod"] != "404":
        msgs = Parallel(n_jobs=3)(delayed(get_forecast_info)(translator, forecast) for forecast in next_forecasts[:20])
    # for forecast in next_forecasts[:20]:
    #         get_forecast_info(translator,forecast)
    await update.message.reply_text(''.join(msgs), parse_mode=ParseMode.HTML)

def get_forecast_info(translator, forecast):
    when = datetime.fromtimestamp(forecast['dt'])
    y = forecast['main']
    temp = round(y["temp"] - 273.15, 2)
    humidity = y["humidity"]
    description = forecast["weather"][0]['description']
    z_translated = translator.translate(description.capitalize())
    return f"<b>{when}</b> -> T: {temp}°C. H: {humidity}%. {z_translated}\n"
'''
[END] WEATHER SECTION
'''

'''
[BEGIN] BICIMAD SECTION
'''
async def get_casa_bikes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = print_results_casa(login_and_get_vals(coordinates=C.coordinates))
    await context.bot.send_message(update.effective_chat.id, message, parse_mode=ParseMode.HTML)
    
async def get_bikes_nearby(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    coordinates = {
        'longitude':  update.message.location.longitude,
        'latitude':  update.message.location.latitude,
    }
    message = print_results(login_and_get_vals(coordinates=coordinates))    
    if message == '':
        message = 'No se han encontrado estaciones cerca! Prueba de nuevo :)' 
    await context.bot.send_message(update.effective_chat.id, message, parse_mode=ParseMode.HTML)

'''
[END] BICIMAD SECTION
'''
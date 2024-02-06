import asyncio
import html
import json
import logging
import os
import shutil
import time
import traceback
import random

from datetime import datetime
from heapq import nlargest, nsmallest

import aiohttp
import matplotlib.pyplot as plt
import numpy as np
import tinytuya
from aiopvpc import PVPCData
from scipy.interpolate import interp1d
from splitwise import Splitwise
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import bot_constants as C


    
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

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
    
async def calentador_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if check_permission(update):
        heater = load_device('calentador')
        if heater.status().get('Error'):
            await update.message.reply_text(f'No es posible conectarse :/')
            return
        elif heater.status().get('dps'):
            await update.message.reply_text(f'Ya está encendido!')
            heater.turn_on()
        else:
           heater.turn_on()
           await update.message.reply_text(f'Calentador ON 🔥')
    else:
        await update.message.reply_text(f'No tienes permiso para emitir esa orden!')
async def calentador_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if check_permission(update):
        heater = load_device('calentador')
        heater.turn_off()
        await update.message.reply_text(f'Calentador OFF ❄️')
    else:
        await update.message.reply_text(f'No tienes permiso para emitir esa orden!')
# async def splitwise_debts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     sObj = Splitwise(C.key, C.consumer_secret, api_key=C.api_key)
#     grupo = [i for i in sObj.getGroups() if i.id==C.SPLITWISE_GROUP_CASA][0]
#     await update.message.reply_text('\n'.join(get_debts(grupo)))
   
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

def load_device(device_name: str) -> tinytuya.OutletDevice:
    # with open(C.DEVICES_FILE, 'r') as d:
    #     devices = json.load(d)
    device_data = [i for i in devices if device_name in i['name'].lower()][0]
    device_ID = device_data['id']
    device_IP = device_data['ip']
    # device_KEY = device_data['key']
    device = tinytuya.OutletDevice(device_ID, device_IP, None,
                                        version=3.3, dev_type='default')
    return device

async def add_subtract(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 1:
        await update.message.reply_text(f'Debes decirme algo que hayas pillau!')
        return
    id = str(update.effective_user.first_name)
    mangue = " ".join(context.args)
    with open(C.SUBTRACTS_FILE,'r+') as f:
        if os.path.getsize(C.SUBTRACTS_FILE) == 0:
           data = {}
        else:
            data = json.load(f)
    with open(C.SUBTRACTS_FILE, "w") as f:
        data[id] = data[id] + '\n' + mangue if id in data else mangue
        json.dump(data, f, indent=4)
    await update.message.reply_text(f'"{mangue}" añadido ;)')
    
async def add_paneo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 1:
        await update.message.reply_text(f'Debes decirme un buen paneo!')
        return
    id = str(update.effective_user.first_name)
    paneo = " ".join(context.args)
    with open(C.PANEOS_FILE,'r+') as f:
        if os.path.getsize(C.SUBTRACTS_FILE) == 0:
           data = {}
        else:
            data = json.load(f)
            
    with open(C.PANEOS_FILE, "w") as f:
        data[id] = data[id] + '\n' + paneo if id in data else paneo
        json.dump(data, f, indent=4)
    await update.message.reply_text(f'"{paneo}" añadido ;)')

async def get_price():  
    async with aiohttp.ClientSession() as session:
        pvpc_handler = PVPCData(session = session, tariff = "2.0TD")
        prices: dict = await pvpc_handler.async_update_all(current_data=None, now=datetime.now())
        prices=prices.sensors['PVPC']
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
    
async def message_price_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if C.BUTTONS_PRICE[0] == update.message.text:
        await get_price_now(update, context)
    if C.BUTTONS_PRICE[1] == update.message.text:
        await get_price_graph(update, context)
    
async def get_price_graph(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    dest_path = os.path.join(C.IMAGE_FOLDER ,f'prices_{datetime.now().strftime("%d-%m-%Y %H_%M_%S")}.png')
    if os.path.exists(dest_path):
        await update.message.reply_photo(dest_path, reply_markup=ReplyKeyboardRemove())
        return
    prices = await asyncio.create_task(get_price())
    y=np.array(list(prices.values()))
    x=np.array(list(prices.keys()))
    cubic_interpolation_model = interp1d(x, y, kind = "cubic")
    X_=np.linspace(x.min(), x.max(), 300)
    Y_=cubic_interpolation_model(X_)
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
    await update.message.reply_photo(dest_path, reply_markup=ReplyKeyboardRemove())

async def reset_subtracts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reset_file(C.SUBTRACTS_FILE)
    
async def reset_paneos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reset_file(C.PANEOS_FILE)
    
def reset_file(file: str) -> None:
    data = {}
    with open(file,'w') as f:
        if not os.path.getsize(file) == 0:
            f.write(json.dumps(data))
            
def consult_file(file: str) -> None:
    if os.stat(file).st_size == 0:
        return 'Lista vacía!'
    with open(file,'r+') as f:
            data = json.load(f)
            text = ''
            for key in data.keys():
                text += f'{key} ha acumulado:\n{data[key]}\n'
            return text

async def consult_subtracts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    answer = consult_file(C.SUBTRACTS_FILE)
    await update.message.reply_text(answer)
    
async def consult_paneos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    answer = consult_file(C.PANEOS_FILE)
    await update.message.reply_text(answer)

def get_debts(grupo):
    mensajes=[]
    for debt in grupo.simplified_debts:
        deudor_name=[i.first_name for i in grupo.members if i.id==debt.fromUser][0]
        deudado_name=[i.first_name for i in grupo.members if i.id==debt.toUser][0]
        mensaje=f"{deudor_name} debe {debt.getAmount()} {debt.currency_code} a {deudado_name}"
        mensajes.append(mensaje)
    return mensajes

async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    await context.bot.send_message(job.chat_id, text=f"Atención, recordatorio!! Recuerda callarte la puta boca :)")

async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    try:
        if len(context.args) < 1:
            await update.effective_message.reply_text("Dime cuantos minutos quieres de espera.")
            return
        due = float(context.args[0]) * 60 * 60 
        if due < 0:
            await update.effective_message.reply_text("Primo no se puede viajar al pasado.")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)

        text = "Recordatorio añadido!"
        if job_removed:
            text += " Anterior recordatorio eliminado."
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Uso: /set <horas>")
        
async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Recordatorio cancelado!" if job_removed else "No tienes recordatorios activos primo"
    await update.message.reply_text(text)

# async def temp_and_humidity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     page = urlopen(C.SERVER_URL)
#     html_bytes = page.read()
#     html = html_bytes.decode("utf-8")
#     if 'error' in html:
#         await update.message.reply_text(f'Parece que hay un error :) Resetear chip\n🍄🍄')
#         return
#     temp_index = html.find("ura:")
#     temp = html[temp_index+5:temp_index+12]
#     hum_index = html.find("iva:")
#     hum = html[hum_index+5:hum_index+9]
#     await update.message.reply_text(f'La temperatura es {temp}\nLa humedad relativa es del {hum}\n🍄🍄')
    

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True
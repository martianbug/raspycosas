import asyncio
import difflib
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
import csv

import tinytuya
from aiopvpc import PVPCData
from scipy.interpolate import interp1d
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import bot_constants as C

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def read_csv_as_list(file_path):
    with open(file_path, 'r') as csvfile:
        data = list(csv.reader(csvfile))[0]
    return data

def save_list_as_csv(data, file_path):
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter = ',')
        # if data:
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
    
# async def calentador_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     if check_permission(update):
#         heater = load_device('calentador')
#         if heater.status().get('Error'):
#             await update.message.reply_text(f'No es posible conectarse :/')
#             return
#         elif heater.status().get('dps'):
#             await update.message.reply_text(f'Ya está encendido!')
#             heater.turn_on()
#         else:
#            heater.turn_on()
#            await update.message.reply_text(f'Calentador ON 🔥')
#     else:
#         await update.message.reply_text(f'No tienes permiso para emitir esa orden!')
        
# async def calentador_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     if check_permission(update):
#         heater = load_device('calentador')
#         heater.turn_off()
#         await update.message.reply_text(f'Calentador OFF ❄️')
#     else:
#         await update.message.reply_text(f'No tienes permiso para emitir esa orden!')
        
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

# def load_device(device_name: str) -> tinytuya.OutletDevice:
#     # with open(C.DEVICES_FILE, 'r') as d:
#     #     devices = json.load(d)
#     device_data = [i for i in devices if device_name in i['name'].lower()][0]
#     device_ID = device_data['id']
#     device_IP = device_data['ip']
#     # device_KEY = device_data['key']
#     device = tinytuya.OutletDevice(device_ID, device_IP, None,
#                                         version=3.3, dev_type='default')
#     return device

async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = []
    if len(context.args) < 1:
        await update.message.reply_text(f'Debes decirme algo para comprar')
        return
    item = ' '.join(context.args[0:]).strip()
    if not os.path.exists(C.ITEMS_FILE):
        save_list_as_csv([], C.ITEMS_FILE)
    with open(C.ITEMS_FILE,'r+') as f:
        if os.path.getsize(C.ITEMS_FILE) == 0:
           data = []
        else:
            data = read_csv_as_list(C.ITEMS_FILE)
            
    with open(C.ITEMS_FILE, "w") as f:
        if item not in set(data):
            data.append(item)        
            save_list_as_csv(data, C.ITEMS_FILE)
        else:
            await update.message.reply_text(f'Ese item ya estaba!')   
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
            await update.message.reply_text(f'Has escrito "{item}" regulín pero lo he encontrado! {closest} eliminado ;)')        
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
    
async def delete_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    items = consult_file_items(C.ITEMS_FILE)
    if not items:
        message = "Lista vacía"
        await update.message.reply_text(message)
        return
    reply_keyboard = [items + ['cancelar']]
    await update.message.reply_text(
        "Elije un item:",
        reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder=""
            ),
        )
    return 1

async def delete_markup_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    item = update.message.text
    data = read_csv_as_list(C.ITEMS_FILE)
    data.remove(item)
    await update.message.reply_text(f'"{item}" eliminado ;)')
    save_list_as_csv(data, C.ITEMS_FILE)
    return 1

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

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True
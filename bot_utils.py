from datetime import datetime
import json
import html
import traceback
import asyncio
import os
from aiopvpc import PVPCData
import aiohttp
from telegram import ReplyKeyboardRemove, Update
from heapq import nlargest, nsmallest
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import numpy as np
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
import logging
import bot_constants as C
import tinytuya

with open(C.DEVICES_FILE, 'r') as d:
    devices = json.load(d)
    
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def check_permission(update: object):
    if str(update.effective_chat.id) not in C.ALLOWED_IDS:
        return False
    return True

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
    plt.title(f'Precios electricidad para el {datetime.now().strftime("%Y-%m-%d")}', fontsize=22)
    plt.ylabel("Precio en €/kWh")
    plt.xlabel("Hora")
    plt.locator_params(nbins=20, axis='x')
    plt.legend(loc=2, prop={'size': 10})
    plt.plot(X_, Y_, 'g')
    plt.savefig(dest_path)
    await update.message.reply_photo(dest_path, reply_markup=ReplyKeyboardRemove())

async def reset_subtracts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = {}
    with open(C.SUBTRACTS_FILE,'w') as f:
        if not os.path.getsize(C.SUBTRACTS_FILE) == 0:
            f.write(json.dumps(data))
            
async def consult_subtracts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if os.stat(C.SUBTRACTS_FILE).st_size == 0:
        await update.message.reply_text('No existen mangues actualmente!')
        return
    with open(C.SUBTRACTS_FILE,'r+') as f:
            data = json.load(f)
            text = ''
            for key in data.keys():
                text += f'{key} ha acumulado:\n{data[key]}\n'
    await update.message.reply_text(text)

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

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True
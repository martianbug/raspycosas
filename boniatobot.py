from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, Updater, filters
import os
from datetime import datetime
import aiohttp
from aiopvpc import PVPCData
import asyncio
from splitwise import Splitwise
import bot_constants as C
import time
from bot_utils import unknown, error_handler
import shutil

async def callback_day(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=C.group_id, text='Boas noites')
def get_debts(grupo):
    mensajes=[]
    for debt in grupo.simplified_debts:
        deudor_name=[i.first_name for i in grupo.members if i.id==debt.fromUser][0]
        deudado_name=[i.first_name for i in grupo.members if i.id==debt.toUser][0]
        mensaje=f"{deudor_name} debe {debt.getAmount()} {debt.currency_code} a {deudado_name}"
        mensajes.append(mensaje)
    return mensajes

async def splitwise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    group_casa_id = 43735949
    sObj = Splitwise(C.key, C.consumer_secret, api_key=C.api_key)
    grupo = [i for i in sObj.getGroups() if i.id==group_casa_id][0]
    msjs= get_debts(grupo)
    for msj in msjs:
        await update.message.reply_text(f'{msj}')
    
async def hola(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Que passsa {update.effective_user.first_name}')

async def chill(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Andreeeea cchiiill reláaajate 😇😚')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Bienvenido al Boniato Bot.\n  \nLos comandos los puedes encontrar abajo ;)')

async def proyector_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if shutil.which('irsend') is None:
        await update.message.reply_text(f'No se puede encender proyector ahora.')
        # loop = asyncio.get_event_loop()
        context.error='Not running in Linux'
        task = asyncio.create_task(error_handler(update, context))
        await task
        pass
    else:
        await update.message.reply_text(f'Encendiendo proyector!')
        os.system("irsend SEND_ONCE BENQ_W1070 KEY_POWER")
    
async def proyector_off(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Encendiendo proyector!')
    os.system("irsend SEND_START BENQ_W1070 KEY_POWER")
    time.sleep(0.5) 
    os.system("irsend SEND_STOP BENQ_W1070 KEY_POWER")
    os.system("irsend SEND_ONCE BENQ_W1070 KEY_POWER")
    
async def get_price():  
    async with aiohttp.ClientSession() as session:
        pvpc_handler = PVPCData(session=session, tariff="2.0TD")
        prices: dict = await pvpc_handler.async_update_all(current_data=None, now=datetime.now())
        prices=prices.sensors['PVPC']
        prices = {k.replace(minute=0,second=0, microsecond=0, tzinfo=None).isoformat(): v for k, v in prices.items()}
        price_now = prices[datetime.now().replace(minute=0,second=0, microsecond=0).isoformat()]
    return price_now

async def get_price_now(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    task = asyncio.create_task(get_price())
    price_now = await task
    if price_now > 0.22:
        await update.message.reply_text(f'Precio de la electricité ahora es {price_now} €/kWh . Esto es algo caro! 💸💴')
    else:
        await update.message.reply_text(f'Precio de la electricité ahora es {price_now} €/kWh. Aprovecha ahora para cosas tochas y ahorrar 🤑')

app = ApplicationBuilder().token("6055412517:AAFpxYgauYw1df_Ak3dcKf86DVs4zsMDTf8").build()
# job_queue = app.job_queue
# job_queue.run_daily(callback_day, 30)


app.add_handler(CommandHandler("holita", hola))
app.add_handler(CommandHandler("chill_andrea", chill))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("proyector_on", proyector_on))
app.add_handler(CommandHandler("precio", get_price_now))
app.add_handler(CommandHandler("splitwise", splitwise))
#Error handling
app.add_error_handler(error_handler)

unknown_handler = MessageHandler(filters.COMMAND, unknown)
app.add_handler(unknown_handler)
print('Bontiato Bot running...')
app.run_polling()
print('Bontiato Bot ended!')
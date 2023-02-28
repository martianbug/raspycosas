from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import os
from datetime import datetime
import aiohttp
from aiopvpc import PVPCData
import asyncio
from splitwise import Expense, Splitwise
import bot_constants as C
import time
from bot_utils import unknown, error_handler
import shutil

async def callback_day(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=C.group_id, text='Boas noites')
def get_debts(grupo):
    mensajes=[]
    for debt in grupo.original_debts:
        deudor_name=[i.first_name for i in grupo.members if i.id==debt.fromUser][0]
        deudado_name=[i.first_name for i in grupo.members if i.id==debt.toUser][0]
        mensaje=f"{deudor_name} debe {debt.getAmount()} {debt.currency_code} a {deudado_name}"
        mensajes.append(mensaje)
    return mensajes

async def splitwise_debts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    sObj = Splitwise(C.key, C.consumer_secret, api_key=C.api_key)
    grupo = [i for i in sObj.getGroups() if i.id==C.SPLITWISE_GROUP_CASA][0]
    msjs= get_debts(grupo)
    await update.message.reply_text('\n'.join(msjs))
   
# async def add_splitwise_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     sObj = Splitwise(C.key, C.consumer_secret, api_key=C.api_key)
#     if len(context.args)<2:
#         await update.message.reply_text(f'Debes decirme primero la descripcion y luego el precio!')
#         return
#     grupo = [i for i in sObj.getGroups() if i.id==C.SPLITWISE_GROUP_CASA][0]
#     description = context.args[0]
#     cost = float(context.args[1])
#     expense=Expense()
#     expense.group_id = C.SPLITWISE_GROUP_CASA
#     expense.description =description
#     expense.cost = cost
#     expense.setUsers = grupo.getMembers()
#     # expense.created_by
#     expens=sObj.createExpense(expense)
#     await update.message.reply_text(f'Gasto añadido {expens}')
    
    
async def hola(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Que passsa {update.effective_user.first_name}')

async def chill(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Andreeeea cchiiill reláaajate 😇😚')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Bienvenido al Boniato Bot.\n  \nLos comandos los puedes encontrar abajo ;)')

async def proyector_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if shutil.which('irsend') is None:
        await update.message.reply_text(f'No se puede encender proyector ahora.')
        # context.error = ContextTypes.DEFAULT_TYPE
        await asyncio.create_task(error_handler(update, context))
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
        prices = {k.hour: v for k, v in prices.items()}
    return prices

async def get_price_now(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from heapq import nsmallest, nlargest
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
    
async def get_price_graph(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    import matplotlib.pyplot as plt
    import numpy as np
    from scipy.interpolate import interp1d
    prices = await asyncio.create_task(get_price())
    dest_path = os.path.join(C.IMAGE_FOLDER ,f'prices_{datetime.now().strftime("%d-%m-%Y %H_%M_%S")}.png')
 
    y=np.array(list(prices.values()))
    x=np.array(list(prices.keys()))
    cubic_interpolation_model = interp1d(x, y, kind = "cubic")
    X_=np.linspace(x.min(), x.max(), 300)
    Y_=cubic_interpolation_model(X_)
    
    plt.rcParams.update({'font.size': 22, 'font.family': 'sans-serif', 'font.sans-serif':'Verdana'})
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
    os.remove(dest_path)
    
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    markup = [[KeyboardButton(i)] for i in C.buttons_price]
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Elije una opción:', reply_markup=ReplyKeyboardMarkup(markup))

async def messageHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if C.buttons_price[0] == update.message.text:
        await get_price_now(update, context)
    if C.buttons_price[1] == update.message.text:
        await get_price_graph(update, context)

app = ApplicationBuilder().token("6055412517:AAFpxYgauYw1df_Ak3dcKf86DVs4zsMDTf8").build()
# job_queue = app.job_queue
# job_queue.run_daily(callback_day, 30)

app.add_handler(CommandHandler("holita", hola))
app.add_handler(CommandHandler("chill_andrea", chill))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("proyector_on", proyector_on))
app.add_handler(CommandHandler("precio", price))
app.add_handler(MessageHandler(filters.Text(C.buttons_price), messageHandler))

app.add_handler(CommandHandler("deudas", splitwise_debts))
# app.add_handler(CommandHandler("add_splitwise", add_splitwise_expense))

#Error handling
app.add_error_handler(error_handler)

unknown_handler = MessageHandler(filters.COMMAND, unknown)
app.add_handler(unknown_handler)
print('Bontiato Bot running...'.center(70))
app.run_polling()
print('Bontiato Bot ended!'.center(70))
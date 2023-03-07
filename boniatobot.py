import asyncio
import os
import shutil
import random
import bot_constants as C
import json
import time
from bot_utils import check_permission, error_handler, get_debts, message_price_handler, unknown
from pythonosc import osc_server
from splitwise import Splitwise
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext

hum = 0

async def callback_day(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=C.GROUP_CHAT_ID, text='Boas noites')

async def hola(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Que passsa {update.effective_user.first_name}')

async def chill(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    frase = random.choice(C.ANDREA_PHRASES)
    await update.message.reply_text(frase)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Bienvenido al Boniato Bot.\n  \nLos comandos los puedes encontrar abajo ;)')

def get_data(address, *args):    
    print(f"{address}: {args}")
    global hum
    hum = args[1]

async def temp_and_humidity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    dispatcher = osc_server.Dispatcher()
    server = osc_server.ThreadingOSCUDPServer((C.ip, C.port),dispatcher)
    dispatcher.map("/data", get_data, server)
    server.server_activate()
    # server.serve_forever()
    # await update.message.reply_text(f'{hum}')
   
async def splitwise_debts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    sObj = Splitwise(C.key, C.consumer_secret, api_key=C.api_key)
    grupo = [i for i in sObj.getGroups() if i.id==C.SPLITWISE_GROUP_CASA][0]
    await update.message.reply_text('\n'.join(get_debts(grupo)))
   
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

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    markup = [[KeyboardButton(i)] for i in C.BUTTONS_PRICE]
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Elije una opción:', reply_markup=ReplyKeyboardMarkup(markup))

async def add_subtract(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 1:
        await update.message.reply_text(f'Debes decirme algo que hayas pillau!')
        return
    id = str(update.effective_user.first_name)
    mangue = context.args[0]
    with open(C.SUBTRACTS_FILE,'r+') as f:
        if os.path.getsize(C.SUBTRACTS_FILE) == 0:
           data = {}
        else:
            data = json.load(f)
    with open(C.SUBTRACTS_FILE, "w") as f:
        data[id] = data[id] + '\n' + mangue if id in data else mangue
        json.dump(data, f, indent=4)
        
async def reset_subtracts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = {}
    with open(C.SUBTRACTS_FILE,'w') as f:
        if not os.path.getsize(C.SUBTRACTS_FILE) == 0:
            data = json.load(f)
            f.write(json.dumps(data))
            
async def consult_subtracts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with open(C.SUBTRACTS_FILE,'r+') as f:
            data = json.load(f)
            text = ''
            for key in data.keys():
                # items = data[key]
                text += f'{key} ha acumulado:\n{data[key]}\n'
    await update.message.reply_text(text)
                
app = ApplicationBuilder().token(C.TOKEN).build()

app.add_handler(CommandHandler("holita", hola))
app.add_handler(CommandHandler("chill_andrea", chill))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("proyector_on", proyector_on))
app.add_handler(CommandHandler("proyector_off", proyector_off))
app.add_handler(CommandHandler("precio", price))
# app.add_handler(CommandHandler("status_setas", temp_and_humidity))
app.add_handler(CommandHandler("mangue", add_subtract))
app.add_handler(CommandHandler("mangue_lista", consult_subtracts))
app.add_handler(CommandHandler("mangue_reset", reset_subtracts))
app.add_handler(CommandHandler("deudas", splitwise_debts))


app.add_handler(MessageHandler(filters.Text(C.BUTTONS_PRICE), message_price_handler))

#Error handling
app.add_error_handler(error_handler)

#unknown_handler = MessageHandler(filters.COMMAND, unknown)
print('Bontiato Bot running...'.center(70))
app.run_polling()
print('Bontiato Bot ended!'.center(70))

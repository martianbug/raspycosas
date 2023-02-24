from telegram import Update
import telegram
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Updater
import os
from datetime import datetime
import aiohttp
from aiopvpc import PVPCData
import asyncio
from splitwise import Splitwise
group_id = '-1001763995292'

async def splitwise(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    sObj = Splitwise("mXTafLpKtojlBiTab15mfAsHyipNMfQVdTKm8B2X","y2wdKYyD7KsU5wlQcarVYrg0K9tvbeEnorFqVQzO")
    session ={}
    session['access_token'] = 'mXTafLpKtojlBiTab15mfAsHyipNMfQVdTKm8B2X'
    sObj.setAccessToken(session['access_token'])
    
    sObj.getFriends()
    url, secret = sObj.getAuthorizeURL()
    oauth_token    = request.args.get('oauth_token')
    oauth_verifier = request.args.get('oauth_verifier')
    # await update.message.reply_text(f'Que passsa {update.effective_user.first_name}')


def callback_minute(context: telegram.ext.CallbackContext):
    context.bot.send_message(chat_id=group_id, 
                             text='One message every day')

async def hola(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Que passsa {update.effective_user.first_name}')

async def chill(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Andreeeea cchiiill reláaajate 😇😚')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Bienvenido al Boniato Bot.\n  \nLos comandos los puedes encontrar abajo ;)')

async def proyector_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Encendiendo proyector!')
    os.system("irsend SEND_ONCE BENQ_W1070 KEY_POWER")
    
async def get_price():  
    async with aiohttp.ClientSession() as session:
        pvpc_handler = PVPCData(session=session, tariff="2.0TD")
        prices: dict = await pvpc_handler.async_update_all(current_data=None, now=datetime.now())
        print(prices)
        prices=prices.sensors['PVPC']
        prices = {k.replace(minute=0,second=0, microsecond=0, tzinfo=None).isoformat(): v for k, v in prices.items()}
        print(prices)
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

# updater = Updater('1605329753:AAGy9Hukl7Nc8CzUJ0tcfndxR_tctvKDCRI', use_context=True)
# dispatcher = updater.dispatcher
# j = updater.job_queue
# job_minute = j.run_repeating(callback_minute, interval=86400, first=10)

app.add_handler(CommandHandler("saludame", hola))
app.add_handler(CommandHandler("chill_andrea", chill))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("proyector_on", proyector_on))
app.add_handler(CommandHandler("precio", get_price_now))


print('Bontiato Bot running...')
app.run_polling()
print('Bontiato Bot ended!')


pass
# get current date
# current_date = datetime.date.today()
# print(current_date)
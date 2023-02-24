from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
from datetime import datetime
import aiohttp
from aiopvpc import PVPCData
import asyncio
from IPython import embed
def get_methods(object, spacing=20):
  methodList = []
  for method_name in dir(object):
    try:
        if callable(getattr(object, method_name)):
            methodList.append(str(method_name))
    except Exception:
        methodList.append(str(method_name))
  processFunc = (lambda s: ' '.join(s.split())) or (lambda s: s)
  for method in methodList:
    try:
        print(str(method.ljust(spacing)) + ' ' +
              processFunc(str(getattr(object, method).__doc__)[0:90]))
    except Exception:
        print(method.ljust(spacing) + ' ' + ' getattr() failed')
        
async def hola(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Que passsa {update.effective_user.first_name}')

async def proyector_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Encendiendo proyector!')
    os.system("irsend SEND_ONCE BENQ_W1070 KEY_POWER")
    
async def get_price():  
    # embed()  
    async with aiohttp.ClientSession() as session:
        print('hasta aqui bien')
        pvpc_handler = PVPCData(session=session, tariff="2.0TD")
        get_methods(PVPCData)
        embed()  
        prices: dict = await pvpc_handler.async_update_prices(datetime.now())
        print('Precios calculados')
        print(prices)
        prices = {k.replace(minute=0,second=0, microsecond=0, tzinfo=None).isoformat(): v for k, v in prices.items()}
        print(prices)
        price_now = prices[datetime.now().replace(minute=0,second=0, microsecond=0).isoformat()]
    return price_now

async def get_price_now(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Calculando precio...')
    task = asyncio.create_task(get_price())
    price_now = await task
    if price_now > 0.22:
        await update.message.reply_text(f'Precio ahora es {price_now} €/kWh . Esto es algo caro!')
    else:
        await update.message.reply_text(f'Precio ahora es {price_now} €/kWh. Ta bien pa una lavadora')

app = ApplicationBuilder().token("6055412517:AAFpxYgauYw1df_Ak3dcKf86DVs4zsMDTf8").build()

app.add_handler(CommandHandler("saludame", hola))
app.add_handler(CommandHandler("proyector_on", proyector_on))
app.add_handler(CommandHandler("precio", get_price_now))

print('Bontiato Bot running...')
app.run_polling()
print('Bontiato Bot ended!')


pass
# get current date
# current_date = datetime.date.today()
# print(current_date)
# if (text == "/start") {
#   String welcome = "Welcome, " + from_name + ".\n";
#   welcome += "Use the following commands to control your outputs.\n\n";
#   welcome += "/led_on to turn GPIO ON \n";
#   welcome += "/led_off to turn GPIO OFF \n";
#   welcome += "/state to request current GPIO state \n";
#   bot.sendMessage(chat_id, welcome, "");
# }
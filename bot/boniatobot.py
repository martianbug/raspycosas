
from urllib.request import urlopen
from bicimad_utils import login_and_get_vals, print_results_casa
import requests
import my_secrets

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (ApplicationBuilder, CallbackContext, CommandHandler,
                          ContextTypes, ConversationHandler, MessageHandler,
                          filters)
from translate import Translator

import bot_constants as C
from bot_utils import *

# ssh martin@192.168.1.20

async def hola(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Que passsa {update.effective_user.first_name}')

# async def movie(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     frase = random.choice(MOVIE)
#     await update.message.reply_text(frase)

def get_data(address, *args):    
    print(f"{address}: {args}")
    global hum
    hum = args[1]

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_keyboard = [[C.BUTTONS_PRICE[0], C.BUTTONS_PRICE[1]]]
    await update.message.reply_text(
        "Elije una opción:",
        reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder=""
            ),
        )
    
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    translator= Translator(from_lang = 'en', to_lang="es", pro = True)
    complete_url = C.URL_WEATHER + "appid=" + C.WEATHER_API_KEY + "&q=" + 'Peña Grande'
    response = requests.get(complete_url)
    x = response.json()
    if x["cod"] != "404":
        y = x["main"]
        temp = round(y["temp"] - 273.15, 2)
        humidity = y["humidity"]
        z = x["weather"][0]['description']
        z_translated = translator.translate(z.capitalize())
    await update.message.reply_text(f"La temperatura en Madrid es {temp} °C, con una humedad del {humidity}%. {z_translated}")


async def get_casa_bikes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = print_results_casa(login_and_get_vals(coordinates=C.coordinates))
    await update.message.reply_text(update.effective_chat.id, message)
    
async def get_bikes_nearby(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    coordinates = {
        'longitude': context.location.longitude,
        'latitude': context.location.latitude,
        'radius': '600'
    }
    message = print_results_casa(login_and_get_vals(coordinates=coordinates))
    await update.message.reply_text(update.effective_chat.id, message)

# @bot.message_handler(func=lambda m: True)
# def print_content(m):
#     print(m)


if __name__ == "__main__":     
    app = ApplicationBuilder().token(my_secrets.TOKEN).build()
    app.add_handler(CommandHandler("holita", hola))
    app.add_handler(CommandHandler("bicimadcasa", get_casa_bikes))
    app.add_handler(CommandHandler("bicimadlocation", get_bikes_nearby))
    
    app.add_handler(CommandHandler("chill_andrea", chill))
    app.add_handler(CommandHandler("proyector_on", proyector_on))
    app.add_handler(CommandHandler("proyector_off", proyector_off))
    app.add_handler(CommandHandler("calentador_on", calentador_on))
    app.add_handler(CommandHandler("calentador_off", calentador_off))
    app.add_handler(CommandHandler("precio", price))
    app.add_handler(CommandHandler("tiempo", weather))
    # app.add_handler(CommandHandler("status_setas", temp_and_humidity))
    app.add_handler(CommandHandler("mangue", add_subtract))
    app.add_handler(CommandHandler("mangue_lista", consult_subtracts))
    app.add_handler(CommandHandler("mangue_reset", reset_subtracts))
    app.add_handler(CommandHandler("paneo", add_paneo))
    app.add_handler(CommandHandler("paneos_lista", consult_paneos))
    app.add_handler(CommandHandler("paneos_reset", reset_paneos))
    # app.add_handler(CommandHandler("deudas", splitwise_debts))
    app.add_handler(MessageHandler(filters.Text(C.BUTTONS_PRICE), message_price_handler))
    app.add_handler(CommandHandler("antiruido", set_timer))
    app.add_handler(CommandHandler("borrar_antiruido", unset))

    app.add_error_handler(error_handler) # error handling
    print('Bontiato Bot running...'.center(70))
    app.run_polling()
    print('Bontiato Bot ended!'.center(70))
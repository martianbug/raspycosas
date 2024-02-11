
from urllib.request import urlopen
from bicimad_utils import login_and_get_vals, print_results, print_results_casa
import requests
import my_secrets
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (ApplicationBuilder, CallbackContext, CommandHandler,
                          ContextTypes, ConversationHandler, MessageHandler,
                          filters)
import bot_constants as C

from bot_utils import *

async def hola(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Que passsa {update.effective_user.first_name}')

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Valeee gracias por comprar ❤️", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply_keyboard = [[C.BUTTONS_PRICE[0], C.BUTTONS_PRICE[1]]]
    await update.message.reply_text(
        "Elije una opción:",
        reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder=""
            ),
        )
    
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

async def switch_sound(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if os.popen("pactl list short modules | grep module-loopback | wc -l").read()[0]=='1':
            await update.message.reply_text(f'Sonido Chromecast onn')
            os.system("pactl unload-module module-loopback")
        else:
            await update.message.reply_text(f'Sonido Chromecast off')
            os.system("pactl load-module module-loopback")

async def max_volume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            await update.message.reply_text(f'Volumen al 100%!!! Cuidaito los vecinos y los oidos ;)')
            os.system("amixer -D pulse sset Master 100%")

async def min_volume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            await update.message.reply_text(f'Volumen al 0%! shhh')
            os.system("amixer -D pulse sset Master 0%")          

async def increase_volume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            await update.message.reply_text(f'Subiendo volumen')
            os.system("amixer -D pulse sset Master 5%+")    

async def decrease_volume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            await update.message.reply_text(f'Subiendo volumen')
            os.system("amixer -D pulse sset Master 5%-")            

async def send_message_group(app, msg):
    await app.bot.sendMessage(chat_id=C.GROUP_CHAT_ID, text=msg)

if __name__ == "__main__":     
    app = ApplicationBuilder().token(my_secrets.TOKEN).build()
    app.add_handler(CommandHandler("holita", hola))
    app.add_handler(CommandHandler("bicimadcasa", get_casa_bikes))
    app.add_handler(MessageHandler(filters.LOCATION, get_bikes_nearby))
    app.add_handler(CommandHandler("sound", switch_sound))
    app.add_handler(CommandHandler("volume_100", max_volume))
    app.add_handler(CommandHandler("volumen_0", min_volume))
    app.add_handler(CommandHandler("volume_up", increase_volume))
    app.add_handler(CommandHandler("volume_down", decrease_volume))
    app.add_handler(CommandHandler("chill_andrea", chill))
    # app.add_handler(CommandHandler("proyector_on", proyector_on))
    # app.add_handler(CommandHandler("proyector_off", proyector_off))
    app.add_handler(CommandHandler("precio", price))
   # app.add_handler(MessageHandler(filters.Text(C.BUTTONS_PRICE), message_price_handler))
    app.add_handler(CommandHandler("tiempo", weather))
    app.add_handler(CommandHandler("tiempo_prediccion", weather_forecast))
    # app.add_handler(CommandHandler("antiruido", set_timer))
    # app.add_handler(CommandHandler("borrar_antiruido", unset))
    app.add_handler(CommandHandler("comprar", add_item))
    app.add_handler(CommandHandler("borrar", delete_item))
    # app.add_handler(CommandHandler("borrar_items", delete_items))
    app.add_handler(CommandHandler("lista_compra", list_items))
    app.add_handler(CommandHandler("compra_reset", reset_items))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("borrar_items", delete_items)],
        allow_reentry = True,
        states={
            DEL_ITEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_markup_item),
                CommandHandler("salir", cancel)],
        },
        fallbacks=[CommandHandler("salir", cancel)])
    app.add_handler(conv_handler)
    app.add_error_handler(error_handler) # error handling
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    app.add_handler(unknown_handler)
    
    print('Bontiato Bot running...'.center(70))
    app.run_polling(allowed_updates = Update.ALL_TYPES)
    print('Bontiato Bot ended!'.center(70))

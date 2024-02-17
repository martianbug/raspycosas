
import my_secrets

import signal
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (ApplicationBuilder, CallbackContext, CommandHandler,
                          ContextTypes, ConversationHandler, MessageHandler,
                          filters)
import bot_constants as C

from bot_utils import *

async def hola(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Que passsa {update.effective_user.first_name}')

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ta prontooo :)")
    os.kill(os.getpid(), signal.SIGINT)
    
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
    
async def switch_sound(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if os.popen("pactl list short modules | grep module-loopback | wc -l").read()[0]=='1':
            await update.message.reply_text(f'Sonido Chromecast onn')
            os.system("pactl unload-module module-loopback")
        else:
            await update.message.reply_text(f'Sonido Chromecast off')
            os.system("pactl load-module module-loopback")

async def set_volumen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 1 or len(context.args[0])>3:
        await update.message.reply_text(f'Debes decirme un número de volumen')
        return
    v = int(context.args[0])
    await update.message.reply_text(f'Volumen al {v}%')
    os.system(f"amixer -D pulse sset Master {v}%")
     
async def speech(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    if len(context.args)<1:
        await update.message.reply_text(f'Pero qué digo???')
        return
    msg = ' '.join(context.args)
    speech_file = text_to_speech(msg)
    # await update.message.reply_text(f'Hablandooo')
    os.system('mpg123 ' + speech_file)

async def spotify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    # if len(context.args)<1:
    #     await update.message.reply_text(f'Pero qué digo???')
    #     return
    # msg = ' '.join(context.args)
    os.system('bot/create_spotify.sh')
    
async def spotify_stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
    # if len(context.args)<1:
    #     await update.message.reply_text(f'Pero qué digo???')
    #     return
    # msg = ' '.join(context.args)
    os.system('sbot/potify_stop.sh')
    
async def increase_volume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            await update.message.reply_text(f'Subiendo volumen')
            os.system("amixer -D pulse sset Master 10%+")    

async def decrease_volume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            await update.message.reply_text(f'Subiendo volumen')
            os.system("amixer -D pulse sset Master 10%-")            

async def send_message_group(app, msg):
    await app.bot.sendMessage(chat_id=C.GROUP_CHAT_ID, text=msg)

if __name__ == "__main__":     
    app = ApplicationBuilder().token(my_secrets.TOKEN).build()
    app.add_handler(CommandHandler("holita", hola))
    app.add_handler(CommandHandler('stop', stop))
    app.add_handler(CommandHandler("bicimadcasa", get_casa_bikes))
    app.add_handler(MessageHandler(filters.LOCATION, get_bikes_nearby))
    app.add_handler(CommandHandler("sound", switch_sound))
    app.add_handler(CommandHandler("volume", set_volumen))
    app.add_handler(CommandHandler("volume_up", increase_volume))
    app.add_handler(CommandHandler("volume_down", decrease_volume))
    app.add_handler(CommandHandler("di", speech))
    app.add_handler(CommandHandler("spotify", spotify))
    app.add_handler(CommandHandler("spotify_stop", spotify_stop))
    
    app.add_handler(CommandHandler("chill_andrea", chill))
    # app.add_handler(CommandHandler("proyector_on", proyector_on))
    # app.add_handler(CommandHandler("proyector_off", proyector_off))
    app.add_handler(CommandHandler("precio", price))
    app.add_handler(MessageHandler(filters.Text(C.BUTTONS_PRICE), message_price_handler))
    app.add_handler(CommandHandler("tiempo", weather))
    app.add_handler(CommandHandler("tiempo_prediccion", weather_forecast))
    app.add_handler(CommandHandler("alarma_lluvia", set_job_rain))
    app.add_handler(CommandHandler("alarma_lluvia_off", unset_jobs))
    app.add_handler(CommandHandler("comprar", add_item))
    app.add_handler(CommandHandler("borrar", delete_item))
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
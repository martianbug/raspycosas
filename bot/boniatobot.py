import my_secrets

import signal
from telegram import  ReplyKeyboardRemove, Update
from telegram.ext import (ApplicationBuilder, CallbackContext, CommandHandler,
                          ContextTypes, ConversationHandler, MessageHandler,
                          filters)
import bot_constants as C

from bot_utils import *
from requests import post

async def hola(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Que passsa {update.effective_user.first_name}')

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ta prontooo :)")
    os.kill(os.getpid(), signal.SIGINT)

async def reboot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Reset!!")
    os.system("sudo reboot")
    
async def cancel_delete_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Valeee gracias por comprar ❤️", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text(';)', reply_markup=ReplyKeyboardRemove()) 
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    return ConversationHandler.END

async def send_message_group(app, msg):
    await app.bot.sendMessage(chat_id=C.GROUP_CHAT_ID, text=msg)

if __name__ == "__main__":     
    app = ApplicationBuilder().token(my_secrets.TOKEN).build()
    app.add_handler(CommandHandler("holita", hola))
    app.add_handler(CommandHandler('stop', stop))
    app.add_handler(CommandHandler('reboot', reboot))
    app.add_handler(CommandHandler('cine', cine_on))
    app.add_handler(CommandHandler('luz', full_light_on))
    app.add_handler(CommandHandler('luz_mesa', mesa_on))
    app.add_handler(CommandHandler('cozy', cozy_on))
    app.add_handler(CommandHandler('leds_studio', leds_studio))
    app.add_handler(CommandHandler('romantic', romantic_on))
    controller_handler = ConversationHandler(
        entry_points=[CommandHandler("mando", controller)],
        allow_reentry = True,
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, control_event),
                CommandHandler("salir", cancel)],
        },
        fallbacks=[CommandHandler("salir", cancel)])
    
    app.add_handler(controller_handler)
    app.add_handler(CommandHandler("bicimadcasa", get_casa_bikes))
    app.add_handler(MessageHandler(filters.LOCATION, get_bikes_nearby))
    app.add_handler(CommandHandler("sound", switch_sound))
    app.add_handler(CommandHandler("volume", set_volumen))
    app.add_handler(CommandHandler("volume_up", increase_volume))
    app.add_handler(CommandHandler("volume_down", decrease_volume))
    app.add_handler(CommandHandler("fail", sad))
    
    app.add_handler(CommandHandler("di", speech))
    app.add_handler(CommandHandler("di_it", speech_italian))
    # app.add_handler(CommandHandler("spotify", spotify))
    # app.add_handler(CommandHandler("spotify_stop", spotify_stop))
    app.add_handler(CommandHandler("chill_andrea", chill))
    # app.add_handler(CommandHandler("proyector_on", proyector_on))
    # app.add_handler(CommandHandler("proyector_off", proyector_off))
    app.add_handler(CommandHandler("precio", price))
    app.add_handler(MessageHandler(filters.Text(C.BUTTONS_PRICE), message_price_handler))
    app.add_handler(CommandHandler("price_reminder", set_job_peak_times))
    app.add_handler(CommandHandler("tiempo", weather))
    app.add_handler(CommandHandler("tiempo_prediccion", weather_forecast))
    app.add_handler(CommandHandler("alarma_lluvia", set_job_rain))
    app.add_handler(CommandHandler("alarma_lluvia_off", unset_jobs))
    app.add_handler(CommandHandler("comprar", add_item))
    app.add_handler(CommandHandler("borrar", delete_item))
    app.add_handler(CommandHandler("lista_compra", list_items))
    app.add_handler(CommandHandler("compra_reset", reset_items))
    items_handler = ConversationHandler(
        entry_points=[CommandHandler("borrar_items", delete_items)],
        allow_reentry = True,
        states={
            DEL_ITEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_markup_item),
                CommandHandler("salir", cancel_delete_items)],
        },
        fallbacks=[CommandHandler("salir", cancel_delete_items)])
    app.add_handler(items_handler)

    app.add_error_handler(error_handler) # error handling
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    app.add_handler(unknown_handler)
    print('Bontiato Bot running...'.center(70))
    app.run_polling(allowed_updates = Update.ALL_TYPES)
    print('Bontiato Bot ended!'.center(70))
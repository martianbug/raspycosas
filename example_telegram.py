from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Que passsa {update.effective_user.first_name}')

async def proyector_on(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    os.system("irsend SEND_ONCE BENQ_W1070 KEY_POWER")
    # await update.message.reply_text(f'Que passsa {update.effective_user.first_name}')


app = ApplicationBuilder().token("6055412517:AAFpxYgauYw1df_Ak3dcKf86DVs4zsMDTf8").build()

app.add_handler(CommandHandler("saludame", hello))
app.add_handler(CommandHandler("proyector_on", proyector_on))


app.run_polling()

pass
# 
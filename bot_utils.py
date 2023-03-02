import json
import html
import traceback
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
import logging
import bot_constants as C
# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )
    await context.bot.send_message(
        chat_id=C.DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
    )

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Lo siento, ese comando no lo conozco")
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

def get_debts(grupo):
    mensajes=[]
    for debt in grupo.original_debts:
        deudor_name=[i.first_name for i in grupo.members if i.id==debt.fromUser][0]
        deudado_name=[i.first_name for i in grupo.members if i.id==debt.toUser][0]
        mensaje=f"{deudor_name} debe {debt.getAmount()} {debt.currency_code} a {deudado_name}"
        mensajes.append(mensaje)
    return mensajes

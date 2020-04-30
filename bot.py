from gtts import gTTS
from bs4 import BeautifulSoup
import json, urllib.request, urllib.parse, re, requests, os

import logging
import configparser
from functools import wraps
from telegram.ext.dispatcher import run_async
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
from telegram import ChatAction,ParseMode, InlineQueryResultArticle, InputTextMessageContent


# variables
BOTNAME = "speakJapaneseBot"
PORT = int(os.environ.get('PORT', '8443'))


# used when sending message to many users simultaneously, like in groups
@run_async
def send_async(bot, *args, **kwargs):
    bot.sendMessage(*args, **kwargs)




# decorator function for bot typing action
def send_typing_action(func):
    """ Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func



# loging utilities
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
logger = logging.getLogger()



# Updater objects
updater = Updater(token=os.environ['token'], use_context=True)
dispatcher = updater.dispatcher




# function to parse the contents of the user's input
def parse(update, context):
    ''' Parse the argumensts '''
    text = ' '.join(context.args)

    # convert the argument in standard uri format
    url_args=urllib.parse.quote(text)
    return url_args



def convert(update, context):
    ''' translating wrapper fro /translate '''
    base_url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=ja&dt=t&q="
    full_url = base_url+parse(update, context)
    # print(full_url)

    # make request to the api to get the json file
    with urllib.request.urlopen(full_url) as response:
        data = json.load(response)
        response.close()
        text=""
        for i in range(len(data[0])):
            # print(data[0][i][0])
            text += data[0][i][0]
    
    return text



# /start option
@send_typing_action
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='''Konichiwa.
Query me some text for translation. 
Use /help whenever stuck.''')



# /translate option
@send_typing_action
def translate(update, context):
    ''' Translate the user's input and make a translated output audio '''
    text = convert(update, context)
    try:
        # translate using gtts module
        output = gTTS(text=text, lang='ja', slow=False) 
        output.save("output/output.mp3")
    except TelegramError:
        logger.debug("TTs API error occured!")

    # reply a text and an audio translated output
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    context.bot.send_voice(chat_id=update.effective_chat.id, voice=open('output/output.mp3', 'rb'))


# /help option
@send_typing_action
def help(update, context):
    ''' Help message '''
    context.bot.send_message(chat_id=update.effective_chat.id, text='''Use the following commands
/start - start message
/translate - translate the message into an audio file
/help - to get this help meassage
''')

####### TO DO
# def inline_caps(update, context):
#     query = update.inline_query.query

#     if not query:
#         return
#     results = list()
#     results.append(
#         InlineQueryResultArticle(
#             id=query.upper(),
#             title='Translate',
#             input_message_content=InputTextMessageContent(convert(update, context))
#         )
#     )
#     context.bot.answer_inline_query(update.inline_query.id, results)



@send_typing_action
def unknown(update, context):
    ''' Manage any unexpected input '''
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")



# Dispatchers
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('translate', translate))
dispatcher.add_handler(CommandHandler('help', help))
# dispatcher.add_handler(InlineQueryHandler(inline_caps))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))


# start the bot using web_hooks instead of polling as:
# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku

updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=os.environ['token'])
updater.bot.set_webhook("https://powerful-lowlands-26874.herokuapp.com/" + os.environ['token'])

# Stop the bot until Ctrl+C is pressed or a signal is sent to the bot process
updater.idle()
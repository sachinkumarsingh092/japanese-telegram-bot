from gtts import gTTS
from bs4 import BeautifulSoup
import json, urllib.request, re, requests, os

import logging
import configparser
from functools import wraps
from telegram.ext.dispatcher import run_async
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler
from telegram import ChatAction,ParseMode, InlineQueryResultArticle, InputTextMessageContent

BOTNAME = "JapaneseBot"

@run_async
def send_async(bot, *args, **kwargs):
    bot.sendMessage(*args, **kwargs)


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func


logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
logger = logging.getLogger()

updater = Updater(token=os.environ['token'], use_context=True)
dispatcher = updater.dispatcher

@send_typing_action
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Use this bot to learn Japanese!")


# text = "i live in london. I love playing table tennis.\
#     This is so much fun."

# ## scrapping 
# # url = "https://translate.google.com/#view=home&op=translate&sl=auto&tl=ja&text="+text
# # page = requests.get(url)
# # soup = BeautifulSoup(page.content, 'html.parser')
# # titles = soup.findAll('div', {'class': 'tlid-transliteration-content.transliteration-content.full'})
# # print(titles)

def parse(update, context):
    text=""
    for _ in context.args:
        temp = re.sub('[^A-Za-z0-9 ]+', '', _)
        text += temp + ' '
    text = re.sub('\.', '+', text)
    ttemp = text.split()
    # print(temp)
    sourceText = '+'.join(ttemp)
    print(sourceText)
    return sourceText

@send_typing_action
def fetch(update, context):
    base_url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=ja&dt=t&q="
    full_url = base_url+parse(update, context)
    print(full_url)
    with urllib.request.urlopen(full_url) as response:
        data = json.load(response)    
        print(data[0][0][0])
    output = gTTS(text=data[0][0][0], lang='ja', slow=False) 
    output.save("output.mp3")
    context.bot.send_message(chat_id=update.effective_chat.id, text=data[0][0][0])
    context.bot.send_voice(chat_id=update.effective_chat.id, voice=open('output.mp3', 'rb'))

# def inline(update, context):
#     query = update.inline_query.query
#     if not query:
#         return
#     results = list()
#     text=parse(update, context)
#     results.append(
#         InlineQueryResultArticle(
#             id=query.upper(),
#             title='Inline',
#             input_message_content=InputTextMessageContent(text)
#         )
#     )
   # context.bot.answer_inline_query(update.inline_query.id, results)


@send_typing_action
def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('fetch', fetch))
# dispatcher.add_handler(InlineQueryHandler(inline))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))


updater.start_polling()
updater.idle()
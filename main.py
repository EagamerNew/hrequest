import sys

from telegram.ext import Updater, InlineQueryHandler, CommandHandler
import requests

import collections

from telegram.ext import Filters
from telegram.ext import MessageHandler


class DialogBot(object):

    def __init__(self, token, generator):
        self.updater = Updater(token=token)  # заводим апдейтера
        handler = MessageHandler(Filters.text | Filters.command, self.handle_message)
        self.updater.dispatcher.add_handler(handler)  # ставим обработчик всех текстовых сообщений
        self.handlers = collections.defaultdict(generator)  # заводим мапу "id чата -> генератор"

    def start(self):
        self.updater.start_polling()

    def handle_message(self, bot, update):
        print("Received", update.message)
        chat_id = update.message.chat_id
        if update.message.text == "/start":
            self.handlers.pop(chat_id, None)
        if chat_id in self.handlers:
            try:
                answer = self.handlers[chat_id].send(update.message)
            except StopIteration:
                del self.handlers[chat_id]
                return self.handle_message(bot, update)
        else:
            answer = next(self.handlers[chat_id])
        print("Answer: %r" % answer)
        bot.sendMessage(chat_id=chat_id, text=answer)

def dialog():
    answer = yield "Hello, my name is HRequestBot and what's your name?"
    name = answer.text.rstrip(".!").split()[0].capitalize()
    likes_python = yield from ask_yes_or_no("Thank you, %s. Would you like to see list of available hospitals?" % name)
    if likes_python:
        answer = yield from discuss_good_python(name)
    else:
        answer = yield from discuss_bad_python(name)


def ask_yes_or_no(question):
    """Спросить вопрос и дождаться ответа, содержащего «да» или «нет».

    Возвращает:
        bool
    """
    answer = yield question
    i =0
    hosplist=['Almaty first hospital','Semei 7ths hospital','Astana 9th hospital', 'Almaty Clinical Hospital']
    while not ("+" in answer.text.lower()):
        answer = yield hosplist[i]
        i+=1
        if i == 3:
            i = 0
    return "+" in answer.text.lower()


def discuss_good_python(name):
    answer = yield "Ok, %s, you chose hospital and next thing is which type of service you need? Type the answer(Ex:dentist,urologist,cardiologist):" % name
    answer = yield "We chat to you later! Thank you!"
    return answer


def discuss_bad_python(name):

    answer = "Oh, no something is wrong! We fix it later!"
    return answer

def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url
def bop(bot, update):
    url = get_url()
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo=url)
def main():
    updater = Updater('mytoken')
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('bop',bop))
    updater.start_polling()
    updater.idle()
if __name__ == '__main__':
    # main()
    dialog_bot = DialogBot('mytoken', dialog)
    dialog_bot.start()
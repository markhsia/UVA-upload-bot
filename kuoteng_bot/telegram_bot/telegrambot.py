#_*_ encoding: utf-8 _*_
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from django_telegrambot.apps import DjangoTelegramBot
from emoji import emojize
#uva upload function
from telegram_bot import uva
import requests
import requests.packages.urllib3

#word2vec
#不該在此引入...不過分開來做load好像不太優
from gensim.models import word2vec
from gensim import models
from gensim.models.keyedvectors import KeyedVectors

#jieba
import jieba
import random
import jieba.posseg as pseg

#database
from telegram_bot.models import User


import logging
logger = logging.getLogger(__name__)

# from .fsm import TocMachine
from transitions.extensions import GraphMachine

import pprint
pp = pprint.PrettyPrinter(indent=4)

machine = GraphMachine(
    states=[
        '()not_have_used_start_to_set',
        '(-1)uva_unenroll_user',
        '(0)uva_enrolled_user',
        '(>-1)upload_file_to_uva',
        '(*)use_start_to_set',
        '(1)want_to_set_uva_id',
        '(2)want_to_set_uva_passwd',
        '(!=1||!=2)echo',
        'set_uva_id',
        'set_uva_passwd',
        'show_fsm'
    ],
    transitions=[
        {
            'trigger': '\\start',
            'source': [
                    '()not_have_used_start_to_set',
                    '(-1)uva_unenroll_user',
                    '(0)uva_unenrolled_user',
                    '(1)want_to_set_uva_id',
                    '(2)want_to_set_uva_passwd'
                ],
            'dest': '(*)use_start_to set',
        },
        {
            'trigger': 'go_back',
            'source': '(*)use_start_to_set',
            'dest': '(-1)uva_unenrolled_user',
            'conditions': 'database states is in -1'
        },
        {
            'trigger': 'go_back',
            'source': '(*)use_start_to_set',
            'dest': '(0)uva_enrolled_user',
            'conditions': 'database states is in 0'
        },
        {
            'trigger': 'go_back',
            'source': '(*)use_start_to_set',
            'dest': '(1)want_to_set_uva_id',
            'conditions': 'database states is in 1'
        },
        {
            'trigger': 'go_back',
            'source': '(*)use_start_to_set',
            'dest': '(2)want_to_set_uva_passwd',
            'conditions': 'database states is in 2'
        },
        {
            'trigger': 'send_text',
            'source': [
                    '()not_have_used_start_to_set',
                    '(-1)uva_unenroll_user',
                    '(0)uva_enrolled_user',
                ],
            'dest': '(!=1||!=2)echo',
            'conditions': 'database states not 1 or 2',
        },
        {
            'trigger': 'send_file',
            'source': '()not_have_used_start_to_set',
            'dest': '()not_have_used_start_to_set',
            'conditions': 'not found in database'
        },
        {
            'trigger': 'send_file',
            'source': '(-1)uva_unenrolled_user',
            'dest': '(-1)uva_unenrolled_user',
            'conditions': 'database states is -1'
        },
        {
            'trigger': 'send_file',
            'source': [
                    '(0)uva_enrolled_user',
                    '(1)want_to_set_uva_id',
                    '(2)want_to_set_uva_passwd'
                ],
            'dest': '(>-1)upload_file_to_uva',
            'conditions': 'database states > -1'
        },
        {
            'trigger': 'go_back',
            'source': '(>-1)upload_file_to_uva',
            'dest': '(0)uva_enrolled_user',
            'conditions': 'database states is in 0'
        },
        {
            'trigger': 'go_back',
            'source': '(>-1)upload_file_to_uva',
            'dest': '(1)want_to_set_uva_id',
            'conditions': 'database states is in 1'
        },
        {
            'trigger': 'go_back',
            'source':  '(>-1)upload_file_to_uva',
            'dest': '(2)want_to_set_uva_passwd',
            'conditions': 'database states is in 2'
        },
        {
            'trigger': 'choose_set_id',
            'source': [
                '(*)use_start_to_set',
                '(-1)uva_unenroll_user',
                '(0)uva_enrolled_user'
                ],
            'dest': '(1)want_to_set_uva_id'
        },
        {
            'trigger': 'choose_set_passwd',
            'source': [
                '(*)use_start_to_set',
                '(-1)uva_unenroll_user',
                '(0)uva_enrolled_user'
            ],
            'dest': '(2)want_to_set_uva_passwd'
        },
        {
            'trigger': 'send_text',
            'source': '(1)want_to_set_uva_id',
            'dest': 'set_uva_id',
            'conditions': 'in states 1'
        },
        {
            'trigger': 'send_text',
            'source': '(2)want_to_set_uva_passwd',
            'dest': 'set_uva_passwd',
            'conditions': 'in states 2'
        },
        {
            'trigger': 'go back',
            'source': [
                    'set_uva_id',
                    'set_uva_passwd'
                ],
            'dest': '(0)uva_enrolled_user'
        },
        {
            'trigger': '/fsm',
            'source': [
                    '()not_have_used_start_to_set',
                    '(-1)uva_unenroll_user',
                    '(0)uva_enrolled_user',
                    '(1)want_to_set_uva_id',
                    '(2)want_to_set_uva_passwd' 
                ],
            'dest': 'show_fsm'
        },
        {
            'trigger': 'go_back',
            'source': 'show_fsm',
            'dest': '()not_have_used_start_to_set',
            'conditions': 'not found in database'
        },
        {
            'trigger': 'go_back',
            'source': 'show_fsm',
            'dest': '(-1)uva_unenrolled_user',
            'conditions': 'database states is -1'
        },
        {
            'trigger': 'go_back',
            'source': 'show_fsm',
            'dest': '(0)uva_enrolled_user',
            'conditions': 'database states is 0'
        },
        {
            'trigger': 'go_back',
            'source': 'show_fsm',
            'dest': '(1)want_to_set_uva_id',
            'conditions': 'database states is 1'
        },
        {
            'trigger': 'go_back',
            'source': 'show_fsm',
            'dest': '(2)want_to_set_uva_passwd',
            'conditions': 'database states is 2'
        }        
    ],
    initial='()not_have_used_start_to_set',
    auto_transitions=False,
    show_conditions=True,
)

# word2vec load


logging.basicConfig(format='%(asctime)s: %(levelname)s : %(message)s', level=logging.INFO)
model = KeyedVectors.load_word2vec_format("med250.model.bin", binary=True)

jieba.set_dictionary('jieba_data/dict.txt.big')

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    try:
        search_id = User.objects.get(telegram_id=update.message.chat.id)
        bot.sendMessage(update.message.chat_id, text='又見面了呢！')
    except:
        search_id = User.objects.create(telegram_id=update.message.chat.id,
                                        first_name=str(update.message.chat.first_name),
                                        last_name=str(update.message.chat.last_name),
                                        username=str(update.message.chat.username))
        bot.sendMessage(update.message.chat_id, text='是第一次見面呢！不過沒關係，我已經記住你的長相了！')
    
    keyboard = [[InlineKeyboardButton("(重新)設定uva帳號", callback_data='1'),
                 InlineKeyboardButton("(重新)設定uva密碼", callback_data='2')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.sendMessage(update.message.chat_id, text='點選以下按鈕讓我更加認識你<3', reply_markup=reply_markup)

def button(bot, update):
    print(update)
    try:
        search_id = User.objects.get(telegram_id=update.callback_query.message.chat.id)
        query = update.callback_query
        if query.data == '1':
            bot.sendMessage(update.callback_query.message.chat.id, text='那麼, 請告訴我你的帳號(Tips:任何下一次輸入字串都視為帳號)')
            search_id.states = 1
            search_id.save()
        else:
            bot.sendMessage(update.callback_query.message.chat.id, text='那麼, 請告訴我你的密碼(Tips:任何下一次輸入字串都視為密碼)')
            search_id.states = 2
            search_id.save()
    except:
        bot.sendMessage(update.callback_query.message.chat.id, text='你還沒有透過/start讓我認識你呢! 做事要按照優先順序呀QQ')

def help(bot, update):
    bot.sendMessage(update.message.chat_id, text='幹!')

def uva_enroll(bot, update):
    try:
        search_id = User.objects.get(telegram_id=update.message.chat.id)
        print(search_id.username)
        print(search_id.uva_id)
        if search_id.states() > -1:
            bot.sendMessage(update.message.chat_id, text='嗨!我還記得你,你最後跟我說的uva帳號是'+search_id.uva_id)
        else:
            bot.sendMessage(update.message.chat_id, text='嗨!你好像沒有跟我說過uva帳號呢')
    except:
        bot.sendMessage(update.message.chat_id, text='你好像沒有透過/start讓我認識你呢!!')


def echo(bot, update):
    try:
        search_id = User.objects.get(telegram_id=update.message.chat_id)
        if search_id.states == 1:
            search_id.uva_id = update.message.text
            logger.info("set the uva_id to %s" % (update.message.text))
            search_id.states = 0
            search_id.save()
            return
        elif search_id.states == 2:
            search_id.uva_passwd = update.message.text
            logger.info("set the uva_passwd")
            search_id.states = 0
            search_id.save()
            return
        else:
            print(search_id)
            print(search_id.states)
            pass
    except:
        logger.info("this person has not used the /start")

    msg = pseg.cut(update.message.text)
    print(msg)
    pp.pprint(msg)
    nword_list = []
    for word,flag in msg:
        print(word,flag)
        if flag.find('n') != -1:
            nword_list.append(str(word))
        elif flag.find('b') != -1:
            nword_list.append(str(word))
    print(nword_list)
    try:
        index = random.randint(0, len(nword_list)-1)
        print(nword_list[index])
        res = model.most_similar(nword_list[index], topn = 1)
        bot.sendMessage(update.message.chat_id, text='你好像在跟我談'+nword_list[index]+'的相關話題')
        for item in res:
            bot.sendMessage(update.message.chat_id, text='你是想說'+item[0]+'的話題嗎?')
    except:
        bot.sendMessage(update.message.chat_id, text='對不起...我的理解力低弱不知道你在講什麼')

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def test(bot, update):
    update.message.reply_text('Hello World!')
    bot.sendPhoto(update.message.chat_id, photo='https://telegram.org/img/t_logo.png')
        #bot.sendPhote(update.message.chat_id, photo=open('/home/kuoteng/toc_project/kuoteng_bot/my_stat_diagram.png','rb'),caption='fuck'.encode('UTF-8'))

def nowDiagram(bot, update):
    machine.graph.draw('my_stat_diagram.png', prog='dot', format='png')
    bot.sendPhoto(update.message.chat_id, photo=open('my_stat_diagram.png','rb'))

def getFile(bot, update):
    try:
        search_id = User.objects.get(telegram_id=update.message.chat.id)
        uva_id = search_id.uva_id
        uva_passwd = search_id.uva_passwd
        file = bot.getFile(update.message.document.file_id)
        file_name = update.message.document.file_name
        number = int(file_name.strip(".cpp").strip('UVA-'))
        
        code = requests.get(file.file_path).content
        bot.sendMessage(update.message.chat_id,
                        text="```"+str(code)+"```",
                        parse_mode=ParseMode.MARKDOWN)
        submission = uva.submit(uva_id,uva_passwd,number,file.file_path)
        if True:
            bot.sendMessage(update.message.chat_id, text='%s 已經上傳' % file_name)
        else:
            bot.sendMessage(update.message.chat_id, text='好像有點錯誤！')
    except:
        bot.sendMessage(update.message.chat_id, text='我不記得你有告訴過我你的uva帳號!')
    

def main():

    logger.info("Loading handlers for telegram bot")
    dp = DjangoTelegramBot.dispatcher
    

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("fsm", nowDiagram))
    dp.add_handler(CommandHandler("uva", uva_enroll))
    dp.add_handler(CommandHandler("getFile", getFile))
    dp.add_handler(CallbackQueryHandler(button))
    # on noncommand i.e message - echo the message on Telegram

    dp.add_handler(MessageHandler(Filters.document, getFile))
    dp.add_handler(MessageHandler([Filters.text], echo))

    # log all errors
    dp.add_error_handler(error)


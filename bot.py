""" RuMongolBot Telegram bot """
# -*- coding: utf-8 -*-

import logging
import json
import config
import telebot
import requests
import pyexchange
import datetime
from telebot import types

logLevel = logging.DEBUG

bot = telebot.TeleBot(config.prodToken)
telebot.logger.setLevel(logging.WARN)

l = logging.getLogger()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
l.setLevel(logLevel)

fileHandler = logging.FileHandler('ergigit_bot.log')
fileHandler.setFormatter(formatter)
l.addHandler(fileHandler)

streamHandler = logging.StreamHandler()
streamHandler.setFormatter(formatter)
l.addHandler(streamHandler)


@bot.inline_handler(lambda query: query.query)
def query_text(inline_query):
	try:
		if translate(inline_query.query) is not None:
			message = render_meeting_room(inline_query.query)
			l.debug(text)
			result = types.InlineQueryResultArticle('1',
			                                        inline_query.query,
			                                        types.InputTextMessageContent(text, parse_mode="Markdown"))
			botan_activate(inline_query, 'inline', True)
		else:
			result = types.InlineQueryResultArticle('1',
			                                        u'\U00002757' + 'Пользователь не найден',
			                                        types.InputTextMessageContent('*Пользователь не найден*',
			                                                                      parse_mode="Markdown"))
		bot.answer_inline_query(inline_query.id, [result], cache_time=10)
	except Exception as e:
		l.debug(e)

# Help message
@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
	"""
	start/help hook
	:param message:
	:return:
	"""
	translate = "_/tr <string>_"
	text = "Hello!\nTo get started you should type {}\n\n".format(translate)
	text += "Привет!\nЧтобы начать введи команду {}\n".format(translate)
	bot.send_message(message.chat.id, text, parse_mode="Markdown")


# About message
@bot.message_handler(commands=['about'])
def handle_about(message):
	"""
	about hook
	:param message:
	:return:
	"""
	text = u'\U0001F3AE ' + '*@ERGigit - Виртуальный помощник*\n\n'
	text += u'\U0001F4A1 ' + 'Бронирование переговорных комнат.\n\n'
	text += u'\U00002709 ' + 'Контакты для связи: [@NurbekYakupov](https://t.me/NurbekYakupov)\n\n'

	bot.send_message(message.chat.id, text, parse_mode="Markdown")


# Unsupported media
@bot.message_handler(content_types=['document', 'audio', 'photo'])
def handle_media(message):
	"""
	media unsupported hook
	:param message:
	:return:
	"""
	text = "Я пока не поддерживаю медиа файлы."
	bot.send_message(message.chat.id, text, parse_mode="Markdown")


# Translate
@bot.message_handler(commands=['meeting', 'mt', 'совещание', 'MEETING'])
def handle_translation(message):
	"""
	translate
	:param message:
	:return:
	"""
	try:
		string = message.text.split(" ", 1)[1]
		l.warning('Request from {} - @{}: {}'.format(message.chat.id,
		                                             message.chat.username,
		                                             string))
		#markup = types.ReplyKeyboardMarkup(row_width=2)


		rooms = types.ReplyKeyboardRemove(row_width=1)
		rooms.row(types.KeyboardButton('ERG-409'), types.KeyboardButton('ERG-411'), types.KeyboardButton('ERG-514'))
		rooms.row(types.KeyboardButton('BTS-Charcoal'), types.KeyboardButton('BTS-Ferrum'), types.KeyboardButton('BTS-Copper'))
		rooms.row(types.KeyboardButton(u'\U000025C0 '+'Отмена'))

		
		#print (config.rooms)
		#print (str([i.split() for i in config.rooms]))
		#markup.add(types.KeyboardButton())
		#markup.add(types.KeyboardButton([str(i.split()) for i in config.rooms]))
#		for i in config.rooms:
#			print (i)
#			markup.add(types.KeyboardButton(i))

		#markup.add(itembtn1, itembtn2, itembtn3)
		#markup.add(config.rooms)
		bot.send_message(message.chat.id, "Выберите переговорную:", reply_markup=rooms)

	except LookupError:
		bot.send_message(message.chat.id, "Попробуйте ввести `/meeting <номер кабинета>`", parse_mode="Markdown")




@bot.message_handler(commands=[u'\U000025C0 '+'Отмена'])
def handle_cancel(message):
	try:
		bot.send_message(message.chat.id, "Ты выбрал отмену", reply_markup=rooms)

	except LookupError:
			bot.send_message(message.chat.id, "Попробуйте ввести `/meeting <номер кабинета>`", parse_mode="Markdown")




@bot.message_handler(commands=['events','calendar','cal','ev'])
def give_events(message):
	# Set up the connection to Exchange
	from pyexchange import Exchange2010Service, ExchangeNTLMAuthConnection

	connection = ExchangeNTLMAuthConnection(url=config.ExchangeUrl,
	                                        username=config.ExchangeUsername,
	                                        password=config.ExchangePassword)

	try:
		service = Exchange2010Service(connection)

		curday = datetime.datetime.now()
		events = my_calendar.list_events(curday, curday)
		events.load_all_details()
		bot.send_message(message.chat.id, events.load_all_details(), parse_mode="Markdown")
	except LookupError:
		bot.send_message(message.chat.id, "Не удалост прочитать Календарь", parse_mode="Markdown")




def translate(message):
	"""
	get user's KPI
	:param username:
	:return:
	"""

	url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=mn&tl=ru&dt=t&q={}'.format(message)
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'
	}
	result = requests.get(url, headers = headers)
	if result.status_code == 200:
		j = json.loads(result.text)
		return j[0][0][0]
	else:
		return {"status": "error"}


@bot.message_handler(content_types=["text"])
def placeholder(message):
	"""
	dummy placeholder
	:param message:
	:return:
	"""
	# l.debug(message)
	pass


# text = '*Команда не поддерживается*'
# bot.send_message(message.chat.id, text, parse_mode="Markdown")


if __name__ == '__main__':
	try:
		bot.polling(none_stop=True)
	except KeyboardInterrupt:
		print('\nTerminated by user request\n')
		exit(0)

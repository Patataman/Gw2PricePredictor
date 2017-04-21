#!/usr/bin/env python

import telebot
from random import randint
from timeSerial.mlp.mlp_class import mlp

print("Entrenando redes")
ann = {'19727': {}, '24325': {}, '24292': {}, '24344': {}, '24289': {}}
ann['19727']['buy'] = mlp('buy', '19727', 12, 700, 15, 0.01)
ann['24325']['buy'] = mlp('buy', '24325', 12, 700, 15, 0.01)
ann['24292']['buy'] = mlp('buy', '24292', 12, 700, 10, 0.01)
ann['24344']['buy'] = mlp('buy', '24344', 12, 500, 20, 0.015)
ann['24289']['buy'] = mlp('buy', '24289', 12, 700, 15, 0.1)
ann['19727']['sell'] = mlp('sell', '19727', 12, 1000, 12, 0.01)
ann['24325']['sell'] = mlp('sell', '24325', 12, 700, 20, 0.01)
ann['24292']['sell'] = mlp('sell', '24292', 12, 700, 15, 0.01)
ann['24344']['sell'] = mlp('sell', '24344', 12, 600, 12, 0.015)
ann['24289']['sell'] = mlp('sell', '24289', 12, 700, 15, 0.02)
print("Redes listas")

API_TOKEN = '278445886:AAG5-R5Vr2BFPt24-HqJjWIf9S9ZVDf7mmc'

OBJECTS = {
	'Leño de madera curtida': {
		'id': '19727',
		'img': "http://www.guildwiki2.es/w/images/3/30/Le%C3%B1o_de_madera_curtida.jpg"
	},
	'Piedra imán de destructor': {
		'id': '24325',
		'img': "http://www.guildwiki2.es/w/images/6/6d/Piedra_im%C3%A1n_de_destructor.jpg"
	},
	'Vial de sangre': {
		'id': '24292',
		'img': "http://www.guildwiki2.es/w/images/8/8f/Vial_de_sangre.jpg"
	},
	'Hueso': {
		'id': '24344',
		'img': "http://www.guildwiki2.es/w/images/8/81/Hueso.jpg"
	},
	'Escama blindada': {
		'id': '24289',
		'img': "http://www.guildwiki2.es/w/images/5/5b/Escama_blindada.jpg"
	},
}

bot = telebot.TeleBot(API_TOKEN, skip_pending=False)
states = {}


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
	items = ""
	for i in OBJECTS:
		items += "- " + i + "\n"
	bot.reply_to(message, """
¡Hola, humano!

Puedes usar los siguientes comandos

/precioactual - devuelve el precio actual de un objeto
/prediccion - devuelve la predicción de un objeto en x horas
/mejormomento - devuelve el mejor momento de compra/venta de un objeto

Los *objetos* que puedes consultar son:\n""" + items, parse_mode="Markdown")


@bot.message_handler(commands=['precioactual'])	# Consultar el precio actual de un objeto
def getcurrentprice(message):
	reply = "¿De qué objeto quieres saber el precio actual?"

	markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)

	for i in OBJECTS:
		markup.add(i)

	states[message.chat.id] = {}
	states[message.chat.id]["prediction"] = "current"
	msg = bot.reply_to(message, reply, reply_markup=markup)
	bot.register_next_step_handler(msg, selectobject)


@bot.message_handler(commands=['prediccion'])	# Consultar el precio en x horas de un objeto
def getpredictedprice(message):
	reply = "¿De qué objeto quieres predecir el precio?"

	markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)

	for i in OBJECTS:
		markup.add(i)

	states[message.chat.id] = {}
	states[message.chat.id]["prediction"] = "prediction"
	msg = bot.reply_to(message, reply, reply_markup=markup)
	bot.register_next_step_handler(msg, selectobject)


@bot.message_handler(commands=['mejormomento'])	# Consultar el mejor momento para comprar o vender
def getbestprice(message):
	reply = "¿De qué objeto quieres conocer el mejor momento de compra o venta?"

	markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)

	for i in OBJECTS:
		markup.add(i)

	states[message.chat.id] = {}
	states[message.chat.id]["prediction"] = "best"
	msg = bot.reply_to(message, reply, reply_markup=markup)
	bot.register_next_step_handler(msg, selectobject)


def selectobject(message):
	try:
		if OBJECTS[message.text]:
			states[message.chat.id]["object"] = message.text

			markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
			markup.add("Comprar")
			markup.add("Vender")

			msg = bot.reply_to(message, "¿Para comprar o para vender?", reply_markup=markup)

			if states[message.chat.id]["prediction"] == "current":
				bot.register_next_step_handler(msg, resultcurrent)
			elif states[message.chat.id]["prediction"] == "prediction":
				bot.register_next_step_handler(msg, selectmodeprediction)
			elif states[message.chat.id]["prediction"] == "best":
				bot.register_next_step_handler(msg, selectmodebest)
		else:
			bot.reply_to(message, 'Objeto no encontrado')
	except Exception as e:
		bot.reply_to(message, 'oooops')


def selectmodeprediction(message):
	try:
		if message.text == "Comprar" or message.text == "Vender":
			mode = "compra" if message.text == "Comprar" else "venta"
			states[message.chat.id]["mode"] = mode

			msg = bot.reply_to(message, "¿Dentro de cuántas horas quieres saber el precio?")
			bot.register_next_step_handler(msg, resultprediction)
		else:
			bot.reply_to(message, 'Modo no encontrado')
	except Exception as e:
		bot.reply_to(message, 'oooops')


def selectmodebest(message):
	try:
		if message.text == "Comprar" or message.text == "Vender":
			mode = "compra" if message.text == "Comprar" else "venta"
			states[message.chat.id]["mode"] = mode

			msg = bot.reply_to(message, "¿En qué límite máximo de horas quieres que realicemos la comprobación?")
			bot.register_next_step_handler(msg, resultbest)
		else:
			bot.reply_to(message, 'Modo no encontrado')
	except Exception as e:
		bot.reply_to(message, 'oooops')


def resultcurrent(message):
	try:
		if message.text == "Comprar" or message.text == "Vender":
			mode = "compra" if message.text == "Comprar" else "venta"
			states[message.chat.id]["mode"] = mode
			bot.send_chat_action(message.chat.id, "typing")
			prediction = makeprediction(mode, OBJECTS[states[message.chat.id]["object"]]["id"], 1)

			reply = "Para el objeto *" + states[message.chat.id]["object"] + "* el valor de *" + mode + "* actual es *" + str(prediction) + " bronces*"

			bot.send_photo(message.chat.id, OBJECTS[states[message.chat.id]["object"]]["img"])
			bot.send_message(message.chat.id, reply, parse_mode="Markdown")
		else:
			bot.reply_to(message, 'Modo no encontrado')
	except Exception as e:
		bot.reply_to(message, 'oooops')


def resultprediction(message):
	try:
		states[message.chat.id]["hours"] = int(message.text)
		bot.send_chat_action(message.chat.id, "typing")
		prediction = makeprediction(states[message.chat.id]["mode"], OBJECTS[states[message.chat.id]["object"]]["id"], states[message.chat.id]["hours"])
		reply = "Para el objeto *" + states[message.chat.id]["object"] + "* el valor de *" + states[message.chat.id]["mode"] + "* dentro de *" + str(states[message.chat.id]["hours"]) + "* horas es *" + str(prediction) + " bronces*"

		bot.send_photo(message.chat.id, OBJECTS[states[message.chat.id]["object"]]["img"])
		bot.send_message(message.chat.id, reply, parse_mode="Markdown")
	except Exception as e:
		bot.reply_to(message, 'oooops')


def resultbest(message):
	try:
		states[message.chat.id]["hours"] = int(message.text)

		values = {}
		bot.send_chat_action(message.chat.id, "typing")
		for i in range(states[message.chat.id]["hours"]):
			bot.send_chat_action(message.chat.id, "typing")
			values[i] = makeprediction(states[message.chat.id]["mode"], OBJECTS[states[message.chat.id]["object"]]["id"], i+1)

		if states[message.chat.id]["mode"] == "compra":
			prediction = values[max(values, key=values.get) ]
			n = max(values, key=values.get)
		else:
			prediction = values[min(values, key=values.get) ]
			n = min(values, key=values.get)

		reply = "Para el objeto *" + states[message.chat.id]["object"] + "* el mejor valor de *" + states[message.chat.id]["mode"] + "* en el rango desde ahora hasta dentro de *" + str(states[message.chat.id]["hours"]) + "* horas es *" + str(prediction) + " bronces* y calculo que será en *" + str(n) + "* horas"

		bot.send_photo(message.chat.id, OBJECTS[states[message.chat.id]["object"]]["img"])
		bot.send_message(message.chat.id, reply, parse_mode="Markdown")
	except Exception as e:
		bot.reply_to(message, 'oooops')


def makeprediction(mode, id, hours):
	# return randint(8, 13)
	return ann[id]["buy" if mode == "compra" else "sell"].predict(hours)

@bot.message_handler(func=lambda message: True)
def nlp(message):
	text = message.text.lower().split(' ')
	if (text.count("ahora") > 0 or text.count("momento") > 0) and text.count("mejor") == 0: #Precio actual
		mode = "venta" if text.count("venta") > 0 else "compra"

		bot.send_chat_action(message.chat.id, "typing")
		prediction = makeprediction(mode, OBJECTS["Hueso"]["id"], 1)

		reply = "Para el objeto *" + "Hueso" + "* el valor de *" + mode + "* actual es *" + str(prediction) + " bronces*"

		bot.send_photo(message.chat.id, OBJECTS["Hueso"]["img"])
		bot.send_message(message.chat.id, reply, parse_mode="Markdown")
	elif (text.count("hoy") > 0) and (text.count("mejor") > 0): # bestmoment
		pass
	else:
		pass

bot.polling()

import telebot
from mg import get_map_cell

bot = telebot.TeleBot('5880264308:AAEFDSO7pjTe2FyhJM_HLXks86oVG3LlIgE')

labirint = telebot.types.InlineKeyboardMarkup()
labirint.row( telebot.types.InlineKeyboardButton('←', callback_data='left'),
			  telebot.types.InlineKeyboardButton('↑', callback_data='up'),
			  telebot.types.InlineKeyboardButton('↓', callback_data='down'),
			  telebot.types.InlineKeyboardButton('→', callback_data='right') )

level = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
level.row(  telebot.types.KeyboardButton("Легкий"),
			telebot.types.KeyboardButton("Средний"),
			telebot.types.KeyboardButton("Сложный") )

maps = {}

def get_map_str(map_cell, player, cols, rows):
	map_str = ""
	for y in range(rows * 2 - 1):
		for x in range(cols * 2 - 1):
			if map_cell[x + y * (cols * 2 - 1)]:
				map_str += "⬛"
			elif (x, y) == player:
				map_str += "🐈"
			elif (x, y) == (rows * 2 - 2, cols * 2 - 2):
				map_str += "🐁"
			else:
				map_str += "⬜"
		map_str += "\n"

	return map_str

@bot.message_handler(commands=['meow'])

def start_message(message):
    bot.send_message(message.chat.id, 'Привет! Выбери уровень сложности.', reply_markup=level)

@bot.message_handler(content_types='text')

def play_message(message):
	cols = 0
	rows = 0
	if message.text == "Легкий" :
		cols = 3
		rows = 3
	if message.text == "Средний" :
		cols = 5
		rows = 5
	if message.text == "Сложный" :
		cols = 7
		rows = 7

	map_cell = get_map_cell(cols, rows)

	user_data = {
		'map': map_cell,
		'x': 0,
		'y': 0,
		'cols' : cols,
		'rows' : rows,
	}

	maps[message.chat.id] = user_data

	bot.send_message(chat_id=message.chat.id, text='Охота на мышь началась!')
	bot.send_message(message.from_user.id, get_map_str(map_cell, (0, 0), cols, rows), reply_markup=labirint)


@bot.callback_query_handler(func=lambda call: True)

def callback_func(query):
	user_data = maps[query.message.chat.id]
	new_x, new_y = user_data['x'], user_data['y']

	if query.data == 'left':
		new_x -= 1
	if query.data == 'right':
		new_x += 1
	if query.data == 'up':
		new_y -= 1
	if query.data == 'down':
		new_y += 1

	if new_x < 0 or new_x > 2 * user_data['cols'] - 2 or new_y < 0 or new_y > user_data['rows'] * 2 - 2:
		return None
	if user_data['map'][new_x + new_y * (user_data['cols'] * 2 - 1)]:
		return None

	user_data['x'], user_data['y'] = new_x, new_y

	if new_x == user_data['cols'] * 2 - 2 and new_y == user_data['rows'] * 2 - 2:
		bot.edit_message_text( chat_id=query.message.chat.id,
							   message_id=query.message.id,
							   text="Мышь поймана!" )
		return None

	bot.edit_message_text( chat_id=query.message.chat.id,
						   message_id=query.message.id,
						   text=get_map_str(user_data['map'], (new_x, new_y), user_data['cols'], user_data['rows']),
						   reply_markup=labirint )

bot.polling(none_stop=True, interval=0)
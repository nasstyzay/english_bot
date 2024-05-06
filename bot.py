import telebot
import random
from telebot import types
from telebot.handler_backends import State, StatesGroup
from telebot.types import ReplyKeyboardRemove


TOKEN = '6769353980:AAGZO-LkvHacmJGzPtY9ySUeA7e7VnhwUc4'
bot = telebot.TeleBot(TOKEN)

class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'

class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()

word_pairs = [
    {"russian_word": "Программист", "target_word": "Programmer", "other_words": ["Developer", "Coder", "Engineer"]},
    {"russian_word": "Атрибуты", "target_word": "Attributes", "other_words": ["Ascribe", "Attach", "Symbols"]},
    {"russian_word": "Переменная", "target_word": "Variable", "other_words": ["Volatile", "Unstable", "Different"]},
    {"russian_word": "Авторизация", "target_word": "Authorization", "other_words": ["Login", "Password", "Authorize"]},
    {"russian_word": "Аутентификация", "target_word": "Authentication","other_words": ["function", "Authen", "Register"]},
    {"russian_word": "Библиотека", "target_word": "library", "other_words": ["Bibliotec", "Lubrury", "Book"]},
    {"russian_word": "Компилятор", "target_word": "Compiler", "other_words": ["Translator", "Composer", "Compilation"]},
    {"russian_word": "Репозиторий", "target_word": "Repository", "other_words": ["Storage", "Warehouse", "Storehouse"]},
    {"russian_word": "Отладка", "target_word": "Debugging", "other_words": ["Debug", "Adjustment", "Debugger"]},
    {"russian_word": "Продукт", "target_word": "Product", "other_words": ["Item", "Goods", "Output"]}
]

@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.send_message(message.chat.id, "Привет! Это бот для обучения английским словам.")
    word_pair = random.choice(word_pairs)
    prepare_and_send_word_choice(message, word_pair)


def prepare_and_send_word_choice(message, word_pair):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    russian_word = word_pair["russian_word"]
    target_word = word_pair["target_word"]
    other_words = word_pair["other_words"]

    buttons = [types.KeyboardButton(word) for word in [target_word] + other_words]
    random.shuffle(buttons)

    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])

    markup.add(*buttons)

    bot.send_message(
        message.chat.id,
        f'Угадай слово для перевода: "{russian_word}"',
        reply_markup=markup
    )

    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = russian_word
        data['other_words'] = other_words
        data['current_word_pair'] = word_pair

@bot.message_handler(state=MyStates.target_word)
def handle_word_guess(message):
    user_data = bot.get_state(message.from_user.id, message.chat.id)
    if user_data and isinstance(user_data, dict) and 'target_word' in user_data:
        if message.text == user_data['target_word']:
            bot.send_message(message.chat.id, "Правильно!🎉", reply_markup=ReplyKeyboardRemove())
        else:
            bot.send_message(message.chat.id, "Неправильно!😢 Правильный ответ: " + user_data['target_word'],
                             reply_markup=ReplyKeyboardRemove())

    bot.set_state(message.from_user.id, None, message.chat.id)
@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if message.text == Command.NEXT:
            start_bot(message)
            return

        target_word = data['target_word']


def add_word(message):
    try:
        parts = message.text.split(',')
        if len(parts) >= 5:
            russian, target, *others = parts
            word_pairs.append({"russian_word": russian.strip(), "target_word": target.strip(),
                               "other_words": [word.strip() for word in others]})
            bot.send_message(message.chat.id, "Слово добавлено успешно.")
        else:
            bot.send_message(message.chat.id, "Не достаточно информации. Попробуйте снова.")
    except Exception as e:
        bot.reply_to(message, f'Произошла ошибка: {e}')

def send_word_choice(message, word_pair):
    markup = types.ReplyKeyboardMarkup(row_width=2)

    russian_word = word_pair["russian_word"]
    target_word = word_pair["target_word"]
    other_words = word_pair["other_words"]

    target_word_btn = types.KeyboardButton(target_word)

    other_words_btn = [types.KeyboardButton(word) for word in other_words]
    buttons = [target_word_btn] + other_words_btn
    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)

def delete_word(message):
    target = message.text.strip()
    to_delete = None
    for i, pair in enumerate(word_pairs):
        if pair["target_word"].lower() == target.lower():
            to_delete = i
            break
    if to_delete is not None:
        del word_pairs[to_delete]
        bot.send_message(message.chat.id, "Слово удалено успешно.")
    else:
        bot.send_message(message.chat.id, "Слово не найдено.")


if __name__ == '__main__':
    print('Bot is running!')
    bot.infinity_polling()
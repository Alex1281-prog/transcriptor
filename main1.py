import telebot
from my_secrets import BOT_API_TOKEN
token = BOT_API_TOKEN
from telebot import types 
from things1 import compliments
bot = telebot.TeleBot(token)

#3 папки где лежат исключения, правила и словарь
from slovar import gr2ph
from codes1 import codes
from exceptions1 import exceptions


#фунцкция для транскрипции слов
#выдает все слова в нижнем регистре, удаляет пробелы и апострофы
def get_transcription(word2tr: str) -> str:
    word2tr = word2tr.lower()
    word2tr = word2tr.replace(" ", "").replace("’", "").replace("'", "")


    # для начала проверяем исключения с конечными согласными

    if word2tr in exceptions:
        return exceptions[word2tr]
    #движок для транскрипции
    result = ""
    i = 0
    while i < len(word2tr):
        current_letter = word2tr[i]
        if current_letter in gr2ph:
            combinations = sorted(gr2ph[current_letter].keys(), key=len, reverse=True)
            rule = None
            for k in combinations:
                if k == word2tr[i:i+len(k)]:
                    rule = codes[gr2ph[current_letter][k]]
                    break
            if rule is not None:
                result += rule[0]
                i += rule[1]
            else:
                h = codes[gr2ph[current_letter]['nicht']]
                result += h[0]
                i += 1
        else:
            result += "_ERROR_"
            
            i += 1
    
    result = result.replace("mm", "m").replace("nn", "n")#для слов по типу homme

    # Удаление  r, если слово оканчивается на er и друг. немые окончания
    if word2tr.endswith("er") and result.endswith("ʁ"):
        result = result[:-1]
    #удаление других немых окончаний(1 буква)
    silent_endings = [ "e", "t", "d", "s", "z", "p", "g", "ks"]
    for ending in silent_endings:
        if result.endswith(ending):
            result = result[:-len(ending)]
    #удаление других немых окончаний(2 буквы которые не читаются)

    for sogl_2 in ["es", "ts", "ds", "ps"]:
        if result.endswith(sogl_2):
            result = result[:-len(sogl_2)]
    #для глаголов в множ числе, которые заканчиваются на ent
    for sogl_3 in ["ent"]:
        if result.endswith(sogl_3):
            result = result[:-len(sogl_3)]
    return result

def  transcription_searcher(word2tr: str, i: int, gr2ph: dict, codes:list) -> list:
     pass

#конпоки для бота
@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_button = types.KeyboardButton("Старт")
    action_button = types.KeyboardButton("Что я умею")
    markup.add(start_button, action_button)
    bot.send_message(message.chat.id, text="Привет, {0.first_name} \nВоспользуйся кнопками".format(message.from_user), reply_markup=markup)

user_waiting_for_word = {}

@bot.message_handler(content_types=['text'])
def buttons(message):
    user_id = message.from_user.id
    if message.text == "Старт":
        user_waiting_for_word[user_id] = True
        bot.send_message(message.chat.id, text="Введите французское слово для транскрипции в МФА:")
    elif message.text == "Что я умею":
        bot.send_message(message.chat.id, text="Я умею транскрибировать французские слова и небольшие фразы – преобразовывать их из письменной формы в МФА.")
    else:
        #  транскрипция всегда, без повторного нажатия кнопки
        ipa = get_transcription(message.text)
        bot.send_message(message.chat.id, text=f"МФА транскрипция: {ipa}")
        user_waiting_for_word[user_id] = True

bot.polling(none_stop=True, interval=0)
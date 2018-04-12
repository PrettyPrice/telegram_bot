import telebotlocal as telebot
import os
from telebotlocal import types
import requests
from pyzbar.pyzbar import decode
from PIL import Image
import sqlite3
import json
import logging
import time
from price_parser import tmp_geting_data
from settings import TOKEN, MIX
from logger import Logger
from basket import Basket
from method_for_db import *
from mixpanel import Mixpanel


dir_path = os.path.dirname(os.path.realpath(__file__))
bot = telebot.TeleBot(TOKEN)
# telebot.logger.setLevel(logging.DEBUG)

logger = Logger()
basket_list = []
mp = Mixpanel(MIX)

location_message = None

# JUST RETURN MARKUP
def get_update_markup(id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Оновити ↩️", callback_data=id))
    return keyboard

def get_price(id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Дізнатись ціну. 🔍", callback_data=id))
    return keyboard

# HANDEL ALL UPDATE QUERY
@bot.callback_query_handler(func=lambda c: True)
def inline(call):
    print("INLINE")
    for result in get_user_results(call.message.chat.id):
        # CHECK IF ID IS RIGHT
        if call.data == result[0]:
            print("BARCODE")
            barcodes = []
            for barcode in barcode_with_result(call.data):
                barcodes.append(barcode[1])

            print(barcodes)
            new_message = Basket.get_result_with_barcode(barcodes)

            if len(list(filter(lambda xy: xy[0] != xy[1], zip(new_message, call.message.text)))) != 0:
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id, text=new_message,
                                      reply_markup=get_update_markup(call.data))
            else:
                bot.answer_callback_query(call.id)

    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, '''Ви фотографуєте штрих-код товара \nі надсилаєте його нам, ми обробляємо його\nі видаємо вам пропозиції від магазинів \nз точними цінами.
    Також нам потрібні ваші дані,а саме ваша місце \nзнаходження для визначення релевантних магазинів.''')


@bot.message_handler(commands=['info'])
def handle_info(message):
    bot.send_message(
        message.chat.id, "HippoPrice - Розпочни економити вже зараз, я допоможу тобі знайти де купувати за найвигіднішою ціною.")

@bot.message_handler(content_types=['location'])
def handle_location(message):
    try:

        # TODO: TEST FOR MULTI USERS !!!
        # FIXME: HIDDEN BUG ?
        global location_message
        # FIXME: HIDDEN BUG ?

        location_message = message
        longitude = message.location.longitude
        latitude = message.location.latitude
        markup = types.ReplyKeyboardRemove(selective=False)
        # markup.add(types.KeyboardButton(u'Дізнатись ціни на товар 👛'))
        bot.send_message(message.chat.id, u"Сфотографуй штрих-код товару та завантажте його сюди. 📷", reply_markup=markup)
        mp.track(message.chat.id, 'Location', {
            'longitude': message.location.longitude,
            'latitude': message.location.latitude
        })

        basket_list_chat_id = [item.chat_id for item in basket_list]
        if message.chat.id not in basket_list_chat_id:
            tmp_basket = Basket(message.chat.id)
            basket_list.append(tmp_basket)

        return (longitude, latitude)

    except Exception as err:
        logger.write_logs(handle_location.__name__, err)

@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        mp.people_set(message.chat.id, {
            '$first_name': message.from_user.first_name,
            '$last_name': message.from_user.last_name,
        })
        mp.track(message.chat.id, 'Starting')
        markup = types.ReplyKeyboardMarkup()
        add_user_to_db(message)
        markup.add(types.KeyboardButton(text=u"Дати доступ до геолокації 🗺️", request_location=True))
        bot.send_message(message.chat.id, u"Нам потрібна ваша геолокація щоб підібрати вірний магазин 🛰️", reply_markup=markup)
    except Exception as err:
        logger.write_logs(handle_start.__name__, err)

@bot.message_handler(func=lambda message: u'Дізнатись ціни на товар 👛' == message.text or u'Додати ще товар ➕' == message.text)
def compare_price(message):
    # for basket in basket_list:
    #     if basket.chat_id == message.chat.id:
    #         if basket.check_basket():
    #             markup.add(types.KeyboardButton(u'Додати ще товар'))
    #             markup.add(types.KeyboardButton(u'Порівняти'))
    #             bot.send_message(message.chat.id, u"Загрузуть фото штрих-коду", reply_markup=markup)
    # else:
    #     bot.send_message(message.chat.id, u"Загрузуть фото штрих-коду", reply_markup=markup)
    mp.track(message.chat.id, 'Compare price')
    # markup.add(types.KeyboardButton(u'Додати ще товар ➕'))
    markup = types.ReplyKeyboardMarkup()
    # bot.send_message(message.chat.id, u"Сфотографуй штрих-код товару та завантажте його сюди. 📷", reply_markup=markup)

@bot.message_handler(content_types=['photo'])
def handle_file(message):
    try:
        if message.photo:

            markup = types.ReplyKeyboardMarkup()
            bot.send_message(message.chat.id, u"Очікуйте результату 🕰️", reply_markup=markup)

            # markup.add(types.KeyboardButton(u'Дізнатись ціну. 🔍'))
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            file = requests.get(
                'https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path))

            with open(dir_path+'/imgs/%s_%s.png' % (file_id, message.chat.id), 'wb') as f:

                f.write(file.content)
                decoded_barcode=decode(Image.open(dir_path+'/imgs/%s_%s.png' % (file_id, message.chat.id)))
                # for basket in basket_list:
                #     if basket.chat_id == message.chat.id and len(basket.barcode_list) < 2:

                # bot.send_message(message.chat.id, u"Оберіть опцію 📱", reply_markup=markup)

                if not decoded_barcode:
                    bot.send_message(message.chat.id, u'Штрих код не знайдено, спробуйте ще раз 😞')
                else:
                    res = tmp_geting_data(str(int(decoded_barcode[0].data)))
                    for basket in basket_list:
                        if basket.chat_id == message.chat.id:
                            basket.counter += 1
                            basket.add(res)
                            basket.add_barcode_to_list(str(int(decoded_barcode[0].data)))

                    # tmp_list = [item.chat_id for item in basket_list]
                    # if message.chat.id not in tmp_list:
                    #     tmp_basket = Basket(message.chat.id)
                    #     tmp_basket.counter += 1
                    #     tmp_basket.add(res)
                    #     tmp_basket.add_barcode_to_list(str(int(decoded_barcode[0].data)))
                    #     basket_list.append(tmp_basket)
                    # time.sleep(5)

                    # print(basket_list)
                    mp.track(message.chat.id, 'Handle file', {
                        'barcode' : str(int(decoded_barcode[0].data))
                    })
                    # bot.send_message(message.chat.id, u"Оберіть Опцію")
            os.remove(dir_path+'/imgs/%s_%s.png' % (file_id, message.chat.id))
            compare_price(message)
    except Exception as err:
        logger.write_logs(handle_file.__name__, err)

# @bot.message_handler(func=lambda message: u'Дізнатись ціну. 🔍' == message.text)
def compare_price(message):
    markup = types.ReplyKeyboardMarkup()

    # print(basket_list)
    markup = types.ReplyKeyboardRemove(selective=False)
    # markup.add(types.KeyboardButton(u'Дізнатись ціни на товар 👛'))
    time.sleep(5)

    # print(basket_list)

    for item in basket_list:
        # print(item.chat_id)
        # print(message.chat.id)

        if item.chat_id == message.chat.id:
            # print(item.basket_list)
            # print(item.barcode_list)
            try:
                longitude = location_message.location.longitude
                latitude = location_message.location.latitude
                location = str(longitude) + ',' + str(latitude)
                # print(location)

                r_id = set_result(message, location)
                associate_brcd_res(r_id, item.barcode_list)
                result = item.get_result()

                # Add extra inline markup with id as result_id
                bot.send_message(message.chat.id, result, reply_markup=get_update_markup(r_id))
                # basket_list.remove(item)
                item.clear_basket()
                mp.track(message.chat.id, 'compare', {
                    'barcode': result
                })
                markup = types.ReplyKeyboardRemove(selective=False)
                # markup.add(types.KeyboardButton(u'Дізнатись ціни на товар 👛'))
                bot.send_message(message.chat.id, u"Сфотографуй штрих-код товару та завантажте його сюди. 📷",
                                 reply_markup=markup)

            except:
                markup = types.ReplyKeyboardMarkup()
                add_user_to_db(message)
                markup.add(types.KeyboardButton(text=u"Дати доступ до геолокації 🗺️", request_location=True))
                bot.send_message(message.chat.id, u"Нам потрібена ваша геолокація щоб підібрати вірний магазин 🛰️", reply_markup=markup)

            # print(r_id)

            # print(r_id)
            # print(get_user_results(message))

while True:
    bot.polling(none_stop=True)


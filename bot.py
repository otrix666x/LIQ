import telebot
from telebot import types
import sqlite3
import time
import random
import datetime
import config, text, keyboard
from datetime import datetime, datetime, timedelta
from pyqiwip2p import QiwiP2P
from pyqiwip2p.types import QiwiCustomer, QiwiDatetime
import requests

#p2p = QiwiP2P(auth_key=config.QIWI_PRIV_KEY)

bot = telebot.TeleBot(config.token)
ref_link = 'https://telegram.me/{}?start={}'

part_ref = 'https://telegram.me/{}?start={}_{}'


@bot.message_handler(commands=['start'])
def start_message(message):
   
    connect = sqlite3.connect('bot.db')
    q = connect.cursor()

    q.execute("""CREATE TABLE IF NOT EXISTS ugc_users(
        id TEXT, usr_name TEXT, data_reg TEXT
    )""")

    q.execute("""CREATE TABLE IF NOT EXISTS profile_info (
        id TEXT, balance INTEGER, count_referal INTEGER,ref TEXT,refs TEXT, ref_link TEXT
    )""")

    q.execute("""CREATE TABLE IF NOT EXISTS info_deposit (
        id TEXT, deposit_to_maining TEXT, deposit_to_traiding TEXT
    )""")
    q.execute("""CREATE TABLE IF NOT EXISTS info_vuvod (
        id TEXT,chat_id INTEGER DEFAULT 0, summ INTEGER, requisites TEXT
    )""")
    q.execute("""CREATE TABLE IF NOT EXISTS info_btc (
        id TEXT, summ INTEGER, user TEXT
    )""")
    q.execute("""CREATE TABLE IF NOT EXISTS info_partner (
        id TEXT, cnt_ref INTEGER, partner_link TEXT
    )""")
    q.execute("""CREATE TABLE IF NOT EXISTS trans (
        id INTEGER PRIMARY KEY,zayavka TEXT, data1 TEXT, summ TEXT
    )""")
    q.execute("""CREATE TABLE IF NOT EXISTS payment_check(
        id TEXT, bill TEXT
    )""")
    q.execute('''CREATE TABLE IF NOT EXISTS qiwi_key(
        qiwi TEXT
    )''')
    

    connect.commit
    userid = str(message.chat.id)
    username = str(message.from_user.username)
    row = q.execute('SELECT * FROM ugc_users WHERE id IS ' + str(userid)).fetchone()
    row1 = q.execute(f"SELECT id FROM profile_info where id = '{userid}'").fetchone()
    row2 = q.execute(f"SELECT id FROM info_deposit where id = '{userid}'").fetchone()
    if row is None:
        now = datetime.now()
        now_date = str(str(now)[:10])
        q.execute("INSERT INTO ugc_users (id,usr_name,data_reg) VALUES ('%s', '%s', '%s')"%(userid,username,now_date))
        connect.commit()
    
    if row1 is None:
        balances = 0
        referals = 0
        ref_links = ref_link.format(config.bot_name, message.chat.id)
        q.execute("INSERT INTO profile_info (id, balance, count_referal, ref_link) VALUES ('%s', '%s','%s', '%s')"%(userid, balances, referals, ref_links))
        if message.text[7:16] != '' and message.text[16:] == "":
            if message.text[7:16] != message.chat.id:
                q.execute("update profile_info set ref = " + str(message.text[7:16])+ " where id = " + str(message.chat.id))
                q.execute("update profile_info set count_referal = count_referal + 1 where id = " + str(message.text[7:16]))
                bot.send_message(message.text[7:16], f'Новый реферал! <a href="tg://user?id={message.chat.id}">{message.chat.first_name}</a>', parse_mode='HTML')

        if message.text[7:] != '' and message.text[16:] != "":
            if message.text[17:] != message.chat.first_name:
                q.execute("update profile_info set refs = " + str(message.text[7:16])+ " where id = " + str(message.chat.id))
                q.execute("update info_partner set cnt_ref = cnt_ref + 1 where id = " + str(message.text[7:16]))
                bot.send_message(message.text[7:16], f'Новый реферал по партнерской программе! <a href="tg://user?id={message.chat.id}">{message.chat.first_name}</a>', parse_mode='HTML')
        connect.commit()
    if row2 is None:
        trading = 0
        maining = 0
        q.execute("INSERT INTO info_deposit (id, deposit_to_maining, deposit_to_traiding) VALUES ('%s', '%s', '%s')"%(userid, maining, trading))
        connect.commit()

    bot.send_message(message.chat.id, f"Перед началом использования бота ознакомьтесь с <a href='https://telegra.ph/Usloviya-soglasheniya-i-pravila-ispolzovaniya-05-19'>условиями пользовательского соглашения</a>",disable_web_page_preview=True,parse_mode="html", reply_markup=keyboard.start_confirm)

@bot.callback_query_handler(func=lambda call: True)
def confirm_answer(call):
    
    if call.data == "agrees":
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        row = q.execute("SELECT * FROM info_partner where id is " + str(call.message.chat.id)).fetchone()
        if row is None:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="👋",parse_mode="html")
            bot.send_message(call.message.chat.id, "Вас приветствует администрация <b>LIQ INVEST</b>",parse_mode="HTML", reply_markup=keyboard.main_menu)
        else:
            bot.send_message(call.message.chat.id, "Вас приветствует администрация <b>LIQ INVEST</b>",parse_mode="HTML", reply_markup=keyboard.partner_menu)
            bot.send_sticker(call.message.chat.id, "CAACAgIAAxkBAAECXdhgtnwoqhoHHSWpFm5tBu2OK_a0sAACywYAAhhC7ghbq3TkbU4hxB8E")


    if call.data == "text":
        msg = bot.send_message(call.message.chat.id, "📩Введите текст для рассылки📩")
        bot.register_next_step_handler(msg, send_all)

    if call.data == "pics":
        art = bot.send_message(call.message.chat.id, f"🌌Введите ссылку на фото с бота @imgurbot_bot🌌")
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        bot.register_next_step_handler(art, captions)
    
    if call.data == "top_up":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите способ пополнения🤑", reply_markup=keyboard.payment_button)


    if call.data == "withdrawpart":
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute("SELECT balance FROM profile_info where id is " + str(call.message.chat.id))
        balik = q.fetchone()[0]
        if int(balik) >= 100:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите платёжную систему для вывода📤", reply_markup=keyboard.withdraw_partner)
        else:
            bot.answer_callback_query(call.id, "❌Минимальная сумма для вывода 100р")

    if call.data == "backpart":
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute("SELECT data_reg FROM ugc_users where id is " + str(call.message.chat.id))
        data_register1 = q.fetchone()[0]
        q.execute("SELECT balance FROM profile_info where id is  " + str(call.message.chat.id))
        balancess = q.fetchone()[0]
        q.execute("SELECT cnt_ref FROM info_partner where id is  " + str(call.message.chat.id))
        referalss = q.fetchone()[0]
        q.execute("SELECT partner_link FROM info_partner where id is "+ str(call.message.chat.id))
        ref_links = q.fetchone()[0]
        q.execute("SELECT deposit_to_maining FROM info_deposit where id is "+ str(call.message.chat.id))
        dep_maining = q.fetchone()[0]
        q.execute("SELECT deposit_to_traiding FROM info_deposit where id is "+ str(call.message.chat.id))
        dep_trading1 = q.fetchone()[0]

        q.close()

        bot.send_message(call.message.chat.id,f"👨‍💻{call.message.chat.first_name}, это ваш партнерский кабинет👨‍💻\n\n"\
            f"🏦Баланс: {balancess}\n\n"\
                f"💵Депозит майнинг: {dep_maining}\n\n"\
                    f"💶Депозит трейдинг: {dep_trading1}\n\n"\
                        f"📊Процентная ставка трейдинг: 1-15% в день\n\n"\
                            f"📈Процентная ставка майнинг: 5% в день\n\n"\
                                f"⏳Дата регистрации: {data_register1}\n\n\n"\
                                    f"🙎‍♂️Количество Ваших рефералов: {referalss}\n"\
                                        f"🔗Ваша партнерская ссылка: {ref_links}\n\n"\
                                            "💰Удачного заработака💰",disable_web_page_preview=True,parse_mode="html", reply_markup=keyboard.profile_partner)
        

        
    
    
    if call.data == "back":
        profile_button = types.InlineKeyboardMarkup()
        withdraw = types.InlineKeyboardButton("Заказать вывод", callback_data="withdraw")
        top_up_balnce = types.InlineKeyboardButton("Пополнить баланс", callback_data="top_up")
        partner = types.InlineKeyboardButton("Стать партнером", callback_data="partner_{}".format(call.message.chat.id))
        profile_button.row(withdraw, top_up_balnce)
        profile_button.row(partner)
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute("SELECT data_reg FROM ugc_users where id is " + str(call.message.chat.id))
        data_register1 = q.fetchone()[0]
        q.execute("SELECT balance FROM profile_info where id is  " + str(call.message.chat.id))
        balancess = q.fetchone()[0]
        q.execute("SELECT count_referal FROM profile_info where id is  " + str(call.message.chat.id))
        referalss = q.fetchone()[0]
        q.execute("SELECT ref_link FROM profile_info where id is "+ str(call.message.chat.id))
        ref_links = q.fetchone()[0]
        q.execute("SELECT deposit_to_maining FROM info_deposit where id is "+ str(call.message.chat.id))
        dep_maining = q.fetchone()[0]
        q.execute("SELECT deposit_to_traiding FROM info_deposit where id is "+ str(call.message.chat.id))
        dep_trading1 = q.fetchone()[0]

        q.close()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"👨‍💻{call.message.chat.first_name}, это ваш личный кабинет👨‍💻\n\n"\
            f"🏦Баланс: {balancess}₽\n\n"\
                f"💵Депозит майнинг: {dep_maining}₽\n\n"\
                    f"💶Депозит трейдинг: {dep_trading1}₽\n\n"\
                        f"📊Процентная ставка трейдинг: 1-15% в день\n\n"\
                            f"📈Процентная ставка майнинг: 5% в день\n\n"\
                                f"⏳Дата регистрации: {data_register1}\n\n\n"\
                                    f"🙎‍♂️Количество Ваших рефералов: {referalss}\n"\
                                        f"🔗Ваша реферальная ссылка: {ref_links}\n\n"\
                                            "💰Удачного заработка💰",disable_web_page_preview=True,parse_mode="html", reply_markup=profile_button)
    

    if call.data == "qiwi":
        summ_to_qiwi = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Тип пополнения QIWI\n"\
            "Введите сумму пополнения в рублях", reply_markup=keyboard.back_to_payment)
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        bot.register_next_step_handler(summ_to_qiwi, payment_form_to_qiwi)

    if call.data == "card":
        summ_to_card = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Тип пополнения Карта\n"\
            "Введите сумму пополнения в рублях", reply_markup=keyboard.back_to_payment)
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        bot.register_next_step_handler(summ_to_card, payment_form_to_card)

    if call.data == "btc":
        summ_to_btc = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Тип пополнения BTC\n"\
            "Введите сумму пополнения в рублях", reply_markup=keyboard.back_to_payment)
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        bot.register_next_step_handler(summ_to_btc, payment_form_to_btc)
    
    if call.data == "calc1":
        send = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Тип инвестирования <b>Майнинг</b>\n\n"\
            "<b>Введите сумму, которую хотите рассчитать:</b>", parse_mode='html')
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        bot.register_next_step_handler(send, count_main)
    
    if call.data == "calc2":
        send = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Тип инвестирования <b>Трейдинг</b>\n\n"\
            "<b>Введите сумму, которую хотите рассчитать:</b>", parse_mode='html')
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        bot.register_next_step_handler(send, count_trade)

    
    if call.data == "main_invest":
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute("SELECT balance FROM profile_info where id is " + str(call.message.chat.id))
        bal = q.fetchone()[0]
        q.close()
        min_dep = 500
        if bal >= min_dep:
            summ_to_dep_main = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Введите сумму для инсвестиции доступно {bal}₽")
            bot.register_next_step_handler(summ_to_dep_main, main_dep)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Ваш баланс меньше минимальной суммы депозита {min_dep}₽", reply_markup=keyboard.minimum_babok)

    if call.data == "trade_invest":
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute("SELECT balance FROM profile_info where id is " + str(call.message.chat.id))
        balik = q.fetchone()[0]
        q.close()
        min_dep1 = 100
        if balik >= min_dep1:
            summ_to_dep_trading = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Введите сумму для инсвестиции доступно {balik}₽")
            bot.register_next_step_handler(summ_to_dep_trading, dep_trading)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Ваш баланс меньше минимальной суммы депозита {min_dep1}₽", reply_markup=keyboard.minimum_babok)


    if call.data == "withdraw":
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute("SELECT balance FROM profile_info where id is " + str(call.message.chat.id))
        balik = q.fetchone()[0]
        if int(balik) >= 100:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите платёжную систему для вывода📤", reply_markup=keyboard.withdraw_button)
        
        else:
            bot.answer_callback_query(call.id, "❌Минимальная сумма для вывода 100р")
    
    if call.data == "qiwi1":
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute("SELECT balance FROM profile_info where id is " + str(call.message.chat.id))
        balik = q.fetchone()[0]
        summ_qiwi = bot.send_message(call.message.chat.id, f"Введите сумму для вывода, доступно на вывод {balik}₽\n"\
            "‼️Минимальная сумма вывода 100₽‼️")
        bot.register_next_step_handler(summ_qiwi, withdraw_qiwi)

    if call.data == "card1":
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute("SELECT balance FROM profile_info where id is " + str(call.message.chat.id))
        balik = q.fetchone()[0]
        summ_card = bot.send_message(call.message.chat.id, f"Введите сумму для вывода, доступно на вывод {balik}₽\n"\
            "‼️Минимальная сумма вывода 100₽‼️")
        bot.register_next_step_handler(summ_card, withdraw_card)

    if call.data == "btc1":
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute("SELECT balance FROM profile_info where id is " + str(call.message.chat.id))
        balik = q.fetchone()[0]
        summ_btc = bot.send_message(call.message.chat.id, f"Введите сумму для вывода, доступно на вывод {balik}₽\n"\
            "‼️Минимальная сумма вывода 500₽‼️")
        bot.register_next_step_handler(summ_btc, withdraw_btc)
    
    if call.data == "eth":
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute("SELECT balance FROM profile_info where id is " + str(call.message.chat.id))
        balik = q.fetchone()[0]
        summ_eth = bot.send_message(call.message.chat.id, f"Введите сумму для вывода, доступно на вывод {balik}₽\n"\
            "‼️Минимальная сумма вывода 500₽‼️")
        bot.register_next_step_handler(summ_eth, withdraw_eth)
    
    if call.data == "last_trans":
        try:
            connect = sqlite3.connect('bot.db')
            q = connect.cursor()
            res = q.execute("SELECT * FROM trans ORDER BY ID DESC").fetchall()
            cnt = 1
            trans = '📤Последние выводы📤\n\n'
            for i in res:
                info = f"{cnt}. #{i[1]} {i[3]}₽ {i[2]}\n"
                cnt +=1
                trans = trans + str(info) + '\n'
                if cnt > 10:
                    break
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=trans)
        except:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="На данный момент ещё не было выводов")
    if call.data == "accmain":
        send = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Введите процент который сегодня будем нащитывать максимально 5%")
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        bot.register_next_step_handler(send, accmain)
    
    if call.data == "acctraid":
        send = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Введите процент который сегодня будем нащитывать от 1 до 15%")
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
        bot.register_next_step_handler(send, acctraid)
    
    if call.data == "stop_spam":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Рассылка отменена")


    
    if call.data == "cancel1":
        userid = str(call.message.chat.id)
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute(f"DELETE FROM payment_check where id = '{userid}'")
        connect.commit()

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Платеж был отменен❌")
    
    if call.data == "reset_payment":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите способ пополнения🤑", reply_markup=keyboard.payment_button)

        
        

    arr = call.data.split("_")

    if arr[0] == "done1":
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        info = q.execute(f"SELECT * FROM info_vuvod where id = '{arr[1]}'").fetchone()
        chat_id = info[1]
        zakaz = info[0]
        q.execute(f"DELETE FROM info_vuvod where id = '{zakaz}'")
        connect.commit()
        q.close()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Заявка №{zakaz} выплачена")
        bot.send_message(info[1], f"Заявка №{zakaz} на вывод выполнена")

    arr = call.data.split("_")

    if arr[0] == "add1":
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        data = q.execute(f"SELECT * FROM info_btc where id = '{arr[1]}'").fetchone()
        chat_id = data[0]
        summ = data[1]
        user_name = data[2]
        q.execute(f"update profile_info set balance = balance + '{summ}' where id = '{chat_id}'")
        connect.commit()
        ref_info = q.execute(f"SELECT ref FROM profile_info where id = '{arr[1]}'").fetchone()[0]
        part_info = q.execute(f"SELECT refs FROM profile_info where id = '{arr[1]}'").fetchone()[0]
        if ref_info is None and part_info is None:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Пользователль @{user_name} получил начисление btc")
            bot.send_message(chat_id, f"Ваш баланс пополнен на {summ}₽")
            q.execute(f"DELETE FROM info_btc where id = '{arr[1]}'")
            connect.commit()
            
        elif part_info is None:
            add_money2 = int(int(summ) * 0.03)
            q.execute(f"update profile_info set balance = balance + '{add_money2}' where id = '{ref_info}'")
            bot.send_message(ref_info, f"Вам начисленно {add_money2}₽ от вашего реферала @{user_name}")
            q.execute(f"DELETE FROM info_btc where id = '{arr[1]}'")
            connect.commit()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Пользователль @{user_name} получил начисление btc")
            bot.send_message(chat_id, f"Ваш баланс пополнено на {summ}₽")
        
        elif ref_info is None:
            add_part = int(int(summ) * 0.15)
            q.execute(f"update profile_info set balance = balance + '{add_part}' where id = '{part_info}'")
            bot.send_message(part_info, f"Вам начисленно {add_part}₽ от вашего реферала @{user_name} по парнтерской программе")
            q.execute(f"DELETE FROM info_btc where id = '{arr[1]}'")
            connect.commit()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Пользователль @{user_name} получил начисление btc")
            bot.send_message(chat_id, f"Ваш баланс пополнено на {summ}₽")
            
       
    
    arr = call.data.split("_")
 
    if arr[0] == "cancel":
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        data = q.execute(f"SELECT * FROM info_btc where id = '{arr[1]}'").fetchone()
        q.execute(f"DELETE FROM info_btc where id = '{arr[1]}'")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Заявка на пополнения отменена")
        bot.send_message(data[0], "Срок действия заявки истек, заявка на пополнения отменена")

    if arr[0] == "partner":
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        row = q.execute("SELECT * FROM info_partner where id is " + str(arr[1])).fetchone()
        if row is None:
            username = str(call.message.chat.username)
            send = bot.send_message(call.message.chat.id, "Введите ссылку на источник вашего трафика")
            bot.clear_step_handler_by_chat_id(call.message.chat.id)
            bot.register_next_step_handler(send, register_partner)
        else:
            bot.send_message(arr[1], "Вы уже являетесь нашим партнером", reply_markup=keyboard.partner_menu)
    
    if arr[0] == "reqconf":
        chat_id = arr[1]
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        row = q.execute("SELECT * FROM info_partner WHERE id IS " + str(chat_id)).fetchone()
        if row is None:
            cnt = 0
            ref_partner = part_ref.format(config.bot_name, arr[1], arr[2])
            q.execute("INSERT INTO info_partner (id, cnt_ref, partner_link) VALUES ('%s', '%s', '%s')"%(chat_id, cnt, ref_partner))
            connect.commit()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Заявка для {arr[2]} подтверждена")
        bot.send_message(arr[1], "Ваша заявка на партнерство подтверждена", reply_markup=keyboard.partner_menu)
    if arr[0] == "qeccenc":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Заявка для {arr[2]} отменена")
        bot.send_message(arr[1], "Ваша заявка на партнерство отменена")
    
    if arr[0] == "check":
        summ = arr[1]
        userid = call.message.chat.id
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        key = q.execute("SELECT * FROM qiwi_key").fetchone()[0]
        p2p = QiwiP2P(auth_key=key)
        info = q.execute(f"SELECT bill FROM payment_check where id = '{userid}'").fetchone()[0]
        stat = p2p.check(bill_id=info).status
        if stat == "PAID":
            q.execute(f"DELETE FROM payment_check where id = '{userid}'")
            q.execute(f"update profile_info set balance = balance + '{summ}' where id = '{userid}'")
            connect.commit()
            ref_info = q.execute(f"SELECT ref FROM profile_info where id = '{userid}'").fetchone()[0]
            part_info = q.execute(f"SELECT refs FrOM profile_info where id = '{userid}'").fetchone()[0]
            if ref_info is None and part_info is None:
                bot.send_message(call.message.chat.id, f"Ваш баланс пополнено на {summ}₽")

            elif part_info is None:
                add_money1 = int(int(summ) * 0.03)
                q.execute(f"update profile_info set balance = balance + '{add_money1}' where id = '{ref_info}'")
                connect.commit()
                bot.send_message(ref_info, f"Вам начисленно {add_money1}₽ от вашего реферала")
                q.close()
                bot.send_message(call.message.chat.id, f"Ваш баланс пополнено на {summ}₽")
            
            elif ref_info is None:
                add_part1 = int(int(summ) * 0.15)
                q.execute(f"update profile_info set balance = balance + '{add_part1}' where id = '{part_info}'")
                connect.commit()
                bot.send_message(part_info, f"Вам начисленно {add_part1}₽ от вашего реферала по партнерской программе")
                q.close()
                bot.send_message(call.message.chat.id, f"Ваш баланс пополнено на {summ}₽")
        else:
            bot.send_message(userid,"Оплата ещё не поступила, попробуйте через несколько секунд")
            time.sleep(2)

    



@bot.message_handler(content_types=['text'])
def answer(message):
    
    if message.text == "👨‍💻Support👨‍💻":
        bot.send_message(message.chat.id, f"Хотите задать вопрос или же столкнулись с какой-то проблемой?\n"\
            f"Тогда пишите мне {config.support}\n"\
                f"<a href = '{config.channel}'>Наш канал</a>\n"\
                    f"<a href = '{config.chat}'>Наш чат</a>\n"\
                        f"<a href = '{config.otzyvy}'>Отзывы</a>\n",disable_web_page_preview=True,parse_mode="html")

    if message.text == "/admin":
        if message.chat.id == config.admin1 or message.chat.id == config.admin2:
            bot.send_message(message.chat.id, "🤡", parse_mode='HTML')
            connect = sqlite3.connect('bot.db')
            q = connect.cursor()
            row = q.execute("SELECT * FROM info_partner where id is " + str(message.chat.id)).fetchone()
            q.close()
            if row is None:
                bot.send_message(message.chat.id,'<b>Привет, админ!</b>', parse_mode='HTML', reply_markup=keyboard.main_menu_admin)
            else:
                bot.send_message(message.chat.id,'<b>Привет, админ!</b>', parse_mode='HTML', reply_markup=keyboard.main_menu_admin2)
            

        else:
            connect = sqlite3.connect('bot.db')
            q = connect.cursor()
            row = q.execute("SELECT * FROM info_partner where id is " + str(message.chat.id)).fetchone()
            q.close()
            if row is None:
                bot.send_message(message.chat.id,"<b>🙅Для вас эта команда недоступна🙅</b>", parse_mode='HTML', reply_markup=keyboard.main_menu)
            else:
                bot.send_message(message.chat.id,"<b>🙅Для вас эта команда недоступна🙅</b>", parse_mode='HTML', reply_markup=keyboard.partner_menu)

    
    if message.text == "🔈Запустить рассылку🔈":
        bot.send_message(message.chat.id,"<b>Как будем рассылать?</b>", parse_mode="HTML",reply_markup=keyboard.spam)
    
    if message.text == "🔧Установить p2p ключ🔧":
        send = bot.send_message(message.chat.id, "Введите ключ киви для p2p")
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(send, reset_key)
        
    if message.text == "🏦Общий банк🏦":
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        all_bank_trade = q.execute(f'SELECT SUM(deposit_to_traiding) FROM info_deposit').fetchone()[0]
        all_bank_main = q.execute(f'SELECT SUM(deposit_to_maining) FROM info_deposit').fetchone()[0]
        all_bank = int(all_bank_trade) + int(all_bank_main)
        bot.send_message(message.chat.id, f"Общая сумма инвестиций: {all_bank} руб.")
        q.close()

    if message.text == "💼Кабинет партнера💼":
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute("SELECT data_reg FROM ugc_users where id is " + str(message.chat.id))
        data_register1 = q.fetchone()[0]
        q.execute("SELECT balance FROM profile_info where id is  " + str(message.chat.id))
        balancess = q.fetchone()[0]
        q.execute("SELECT cnt_ref FROM info_partner where id is  " + str(message.chat.id))
        referalss = q.fetchone()[0]
        q.execute("SELECT partner_link FROM info_partner where id is "+ str(message.chat.id))
        ref_links = q.fetchone()[0]
        q.execute("SELECT deposit_to_maining FROM info_deposit where id is "+ str(message.chat.id))
        dep_maining = q.fetchone()[0]
        q.execute("SELECT deposit_to_traiding FROM info_deposit where id is "+ str(message.chat.id))
        dep_trading1 = q.fetchone()[0]
        q.close()

        bot.send_message(message.chat.id,f"👨‍💻{message.chat.first_name}, это ваш партнерский кабинет👨‍💻\n\n"\
            f"🏦Баланс: {balancess}₽\n\n"\
                f"💵Депозит майнинг: {dep_maining}₽\n\n"\
                    f"💶Депозит трейдинг: {dep_trading1}₽\n\n"\
                        f"📊Процентная ставка трейдинг: 1-15% в день\n\n"\
                            f"📈Процентная ставка майнинг: 5% в день\n\n"\
                                f"⏳Дата регистрации: {data_register1}\n\n\n"\
                                    f"🙎‍♂️Количество Ваших рефералов: {referalss}\n"\
                                        f"🔗Ваша партнерская ссылка: {ref_links}\n\n"\
                                            "💰Удачного заработка💰",disable_web_page_preview=True,parse_mode="html", reply_markup=keyboard.profile_partner)

    if message.text == "🖥Личный кабинет🖥":
        profile_button = types.InlineKeyboardMarkup()
        withdraw = types.InlineKeyboardButton("Заказать вывод", callback_data="withdraw")
        top_up_balnce = types.InlineKeyboardButton("Пополнить баланс", callback_data="top_up")
        partner = types.InlineKeyboardButton("Стать партнером", callback_data="partner_{}".format(message.chat.id))
        profile_button.row(withdraw, top_up_balnce)
        profile_button.row(partner)

        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute("SELECT data_reg FROM ugc_users where id is " + str(message.chat.id))
        data_register1 = q.fetchone()[0]
        q.execute("SELECT balance FROM profile_info where id is  " + str(message.chat.id))
        balancess = q.fetchone()[0]
        q.execute("SELECT count_referal FROM profile_info where id is  " + str(message.chat.id))
        referalss = q.fetchone()[0]
        q.execute("SELECT ref_link FROM profile_info where id is "+ str(message.chat.id))
        ref_links = q.fetchone()[0]
        q.execute("SELECT deposit_to_maining FROM info_deposit where id is "+ str(message.chat.id))
        dep_maining = q.fetchone()[0]
        q.execute("SELECT deposit_to_traiding FROM info_deposit where id is "+ str(message.chat.id))
        dep_trading1 = q.fetchone()[0]

        q.close()

        bot.send_message(message.chat.id,f"👨‍💻{message.chat.first_name}, это ваш личный кабинет👨‍💻\n\n"\
            f"🏦Баланс: {balancess}₽\n\n"\
                f"💵Депозит майнинг: {dep_maining}₽\n\n"\
                    f"💶Депозит трейдинг: {dep_trading1}₽\n\n"\
                        f"📊Процентная ставка трейдинг: 1-15% в день\n\n"\
                            f"📈Процентная ставка майнинг: 5% в день\n\n"\
                                f"⏳Дата регистрации: {data_register1}\n\n\n"\
                                    f"🙎‍♂️Количество Ваших рефералов: {referalss}\n"\
                                        f"🔗Реферальная ссылка: {ref_links}\n\n"\
                                            "💰Удачного заработка💰",disable_web_page_preview=True,parse_mode="html", reply_markup=profile_button)
    
    if message.text == "💸Инвестировать💸":
        bot.send_message(message.chat.id,"📈Выберите тип инвестиций📈", reply_markup=keyboard.invest_button)
    
    if message.text == "⚙️Сделать backup⚙️":
        try:
            file_bd = open("bot.db", "rb")
            bot.send_document(config.vuvod, file_bd)
            file_bd.close()
            bot.send_message(message.chat.id, "backup был успешно выгружен ✅")
        except Exception as e:
            bot.send_message(config.error_chat, "!!!Ошибка не получилось сделать backup!!!\n"\
            f"{e}")
            bot.send_message(message.chat.id, "Ошибка")

    
    if message.text == "📠Калькулятор📠":
        send = bot.send_message(message.chat.id, "В данном разделе вы можете рассчитать вашу прибыль от суммы инвестиции.\n\n<b>Выберите тип инвестиции:</b>", parse_mode="html", reply_markup=keyboard.calculate)
    

    if message.text == "⚙️Майнинг⚙️":
        bot.send_message(message.chat.id, text.mining_text, reply_markup=keyboard.maining_button)

    if message.text == "📊Трейдинг📊":
        bot.send_message(message.chat.id, text.trading_text, reply_markup=keyboard.traid_button)

    if message.text == "🔙В главное меню🔙":
        bot.send_message(message.chat.id, "🎇", reply_markup=keyboard.main_menu)

    if message.text == "💲Сделать начисления💲":
        bot.send_message(message.chat.id,"<b>Куда начисляем?</b>", parse_mode='html', reply_markup=keyboard.accruals)
    
    if message.text == "ℹ️Статистикаℹ️":
        key = types.InlineKeyboardMarkup()
        key.row(types.InlineKeyboardButton("Условия", url="https://telegra.ph/Usloviya-soglasheniya-i-pravila-ispolzovaniya-05-19"), types.InlineKeyboardButton("Последние выводы", callback_data="last_trans"))
        req = requests.get("https://yobit.net/api/3/ticker/btc_usd")
        response = req.json()
        sell_price = response["btc_usd"]["sell"]
        btc_price = int(sell_price)

        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        all_user_count = q.execute(f'SELECT COUNT(id) FROM ugc_users').fetchone()[0]
        online = random.randint(0, all_user_count)
        bot.send_message(message.chat.id,"<b>Статистика бота</b>\n\n"\
            "<i>Здесь вы можете ознакомиться с актуальной информацией о количестве  инвесторов и о текущем курсе Bitcoin, который мы используем для  расчета процентной ставки</i>\n\n"\
                f"📈 Курс BitCoin (Yobit): {btc_price} $\n\n"\
                    f"▪️ Всего инвесторов: {all_user_count }\n"\
                        f"▪️ Онлайн: {online}", parse_mode='html', reply_markup=key)




def send_all(message):
    try:
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute("SELECT id FROM ugc_users")
        results = q.fetchall()
        q.close()
        bot.send_message(message.chat.id, "<b>Рассылка начнеться через 10 секунд</b>", parse_mode='html')
        time.sleep(10)
        bot.send_message(message.chat.id, "<b>Рассылка пошла...</b>", parse_mode='html')
        k = 0
        for result in results:
            try:
                bot.send_message(result[0], message.text, parse_mode='html')
            except:
                pass
            time.sleep(0.3)
            k +=1
        bot.send_message(message.chat.id, f"Рассылку получило {str(k)} человек")
    except Exception as e:
        bot.send_message(config.error_chat, "!!!Ошибка РАССЫЛКА ТЕКСТА!!!\n"\
            f"{e}")
        bot.send_message(message.chat.id, "Ошибка рассылки!")

        

        


def captions(message):
    photo = message.text
    text = bot.send_message(message.chat.id, "Введите текст под фото")
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.register_next_step_handler(text, send_photo, photo)

def send_photo(message, photo):
    try:
        text = message.text
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute("SELECT id FROM ugc_users")
        results = q.fetchall()
        q.close()
        bot.send_message(message.chat.id, "<b>Рассылка начнеться через 10 секунд</b>", parse_mode='html')
        time.sleep(10)
        bot.send_message(message.chat.id, "<b>Рассылка пошла...</b>", parse_mode='html')
        k = 0
        for result in results:
            try:
                bot.send_photo(result[0], photo, caption=f"{text}", parse_mode='html')
            except:
                pass
            time.sleep(0.3)
            k += 1
        bot.send_message(message.chat.id, f"Рассылку получило {str(k)} человек")
    except Exception as e:
        bot.send_message(config.error_chat, "!!!Ошибка РАССЫЛКА ФОТО!!!\n"\
            f"{e}")
        bot.send_message(message.chat.id, "Ошибка рассылки!")

def payment_form_to_qiwi(message):
    if message.text.isdigit():
        if int(message.text) <= 50000:
            try:
                connect = sqlite3.connect('bot.db')
                q = connect.cursor()
                key = q.execute("SELECT * FROM qiwi_key").fetchone()[0]
                p2p = QiwiP2P(auth_key=key)
                userid = message.chat.id
                summ = int(message.text)
                new_bill = p2p.bill(amount=summ, lifetime=15)
                info = new_bill.bill_id
                url_qiwi = new_bill.pay_url
                row = q.execute("SELECT * FROM payment_check where id is " + str(userid)).fetchone()
                if row is None:
                    q.execute("INSERT INTO payment_check (id, bill) VALUES ('%s', '%s')"%(userid, info))
                    connect.commit()
                
                else:
                    q.execute(f"DELETE FROM payment_check where id = '{userid}'")
                    connect.commit()
                    q.execute("INSERT INTO payment_check (id, bill) VALUES ('%s', '%s')"%(userid, info))
                    connect.commit()


                #############################################################################################################
                btn = types.InlineKeyboardMarkup()
                btn2 = types.InlineKeyboardButton("Проверить платеж⚙️", callback_data='check_{}'.format(summ))
                btn3 = types.InlineKeyboardButton("Отменить платеж❌", callback_data='cancel1')
                btn.row(btn2, btn3)
                #############################################################################################################


                bot.send_message(message.chat.id,"<b>Ссылка действительна 15 минут</b>\n"\
                    f'<a href="{url_qiwi}">Ваша ссылка на быстрое пополнения баланса</a>', parse_mode='html', reply_markup=btn)
            except Exception as e:
                bot.send_message(config.error_chat, "!!!ОШИБКА ПОПОЛНЕНИЯ КИВИ!!!\n"\
                    f"{e}")
                bot.send_message(message.chat.id, "Ошибка пополнения, попробуйте позже")
        else:
            bot.send_message(message.chat.id, "⛔️ Максимальная сумма одного платежа 50 000₽")
        

    else:
        bot.send_message(message.chat.id, "⛔️ Вы ввели не корректные данные для пополнения. Пополнения закрыто")



    

def payment_form_to_card(message):
    if message.text.isdigit():
        if int(message.text) <= 50000:
            try:
                connect = sqlite3.connect('bot.db')
                q = connect.cursor()
                key = q.execute("SELECT * FROM qiwi_key").fetchone()[0]
                p2p = QiwiP2P(auth_key=key)
                summ_card = int(message.text)
                userid = message.chat.id
                new_bill = p2p.bill(amount=summ_card, lifetime=15)
                info = new_bill.bill_id
                url_card = new_bill.pay_url
                row = q.execute("SELECT * FROM payment_check where id is " + str(userid)).fetchone()
                if row is None:
                    q.execute("INSERT INTO payment_check (id, bill) VALUES ('%s', '%s')"%(userid, info))
                    connect.commit()
                else:
                    q.execute(f"DELETE FROM payment_check where id = '{userid}'")
                    connect.commit()
                    q.execute("INSERT INTO payment_check (id, bill) VALUES ('%s', '%s')"%(userid, info))
                    connect.commit()

                #############################################################################################################
                btn = types.InlineKeyboardMarkup()
                btn2 = types.InlineKeyboardButton("Проверить платеж⚙️", callback_data='check_{}'.format(summ_card))
                btn3 = types.InlineKeyboardButton("Отменить платеж❌", callback_data='cancel1')
                btn.row(btn2, btn3)
                #############################################################################################################


                bot.send_message(message.chat.id, "<b>Ссылка действительна 15 минут</b>\n"\
                    f'<a href="{url_card}">Ваша ссылка на быстрое пополнения баланса</a>', parse_mode='html', reply_markup=btn)
            except Exception as e:
                bot.send_message(config.error_chat, "!!!ОШИБКА ПОПОЛНЕНИЯ КАРТЫ!!!\n"\
                    f"{e}")
                
                bot.send_message(message.chat.id, "Ошибка пополнения, попробуйте позже")
        else:
            bot.send_message(message.chat.id, "⛔️ Максимальная сумма одного платежа 50 000₽")


        
        
    else:
        bot.send_message(message.chat.id, "⛔️ Вы ввели не корректные данные для пополнения. Пополнения закрыто")



def  payment_form_to_btc(message):
    if message.text.isdigit():
        if 500 <= int(message.text) <= 100000:
            try:
                connect = sqlite3.connect('bot.db')
                q = connect.cursor()
                userid = str(message.chat.id)
                user_name = message.chat.username
                summ_rub = int(message.text)
                req = requests.get("https://yobit.net/api/3/ticker/btc_usd")
                response = req.json()
                sell_price = int(response["btc_usd"]["sell"])
                sell_price_rub = sell_price * config.dollar_rate
                sum_btc = summ_rub / sell_price_rub
                sum_btc = float('{:.8f}'.format(sum_btc))
                
                key_add = types.InlineKeyboardMarkup()
                key1 = types.InlineKeyboardButton("Подтвердить", callback_data="add1_{}".format(message.chat.id))
                key2 = types.InlineKeyboardButton("Отменить", callback_data="cancel_{}".format(message.chat.id))
                key_add.row(key1,key2)
                q.execute("INSERT INTO info_btc (id, summ, user) VALUES ('%s', '%s', '%s')"%(userid, summ_rub, user_name))
                connect.commit()
                
                bot.send_message(message.chat.id, "Информация об оплате\n"\
                    f"🔄Курс конвертации: {sell_price_rub} руб\n"\
                        f"🔄BTC адрес: {config.btc_adress}\n\n"\
                            f"Переведите на указанный адрес {sum_btc} btc.\nПосле 1 подтверждения транзакции, деньги поступят вам на баланс")
                
                bot.send_message(config.vuvod, "Запрос на пополнения btc\n"\
                    f"username @{user_name}\n"\
                        f"Сумма в рублях {summ_rub}\n"\
                            f"Сумма в btc {sum_btc}", reply_markup=key_add)
            except Exception as e:
                bot.send_message(config.error_chat, "!!!ОШИБКА ПОПОЛНЕНИЯ BTC!!!\n"\
                    f"{e}")
                bot.send_message(message.chat.id,"Ошибка пополнения, попробуйте позже")
        else:
            bot.send_message(message.chat.id, "⛔️ Максимальная сумма одного платежа 100 000₽\n"\
                "⛔️ Минимальная сумма одного платежа 500₽")


    else:
        bot.send_message(message.chat.id, "⛔️ Вы ввели не корректные данные для пополнения. Пополнения закрыто")
        



def main_dep(message):
    if message.text.isdigit():
        try:
            userid = str(message.chat.id)
            maining_dep = int(message.text)
            min_dep = 500
            if maining_dep >= min_dep:
                connect = sqlite3.connect('bot.db')
                q = connect.cursor()
                q.execute(f"update info_deposit set deposit_to_maining = deposit_to_maining + '{maining_dep}' where id = '{userid}'")
                q.execute(f"update profile_info set balance = balance - '{maining_dep}' where id = {userid}")
                connect.commit()
                row = q.execute("SELECT * FROM info_partner where id is " + str(message.chat.id)).fetchone()
                q.close()
                if row is None:
                    bot.send_message(message.chat.id, f"Было успешно инвестировано {maining_dep}₽ в майнинг", reply_markup=keyboard.main_menu)
                else:
                    bot.send_message(message.chat.id, f"Было успешно инвестировано {maining_dep}₽ в майнинг", reply_markup=keyboard.partner_menu)
            else:
                new_dep = bot.send_message(message.chat.id, f"Минимальная сумма депозита {min_dep}")
                bot.clear_step_handler_by_chat_id(message.chat.id)
                bot.register_next_step_handler(new_dep, main_dep)
        except Exception as e:
            bot.send_message(config.error_chat, "!!!Ошибка!!!\n"\
                f"{e}")
            bot.send_message(message.chat.id, "Ошибка, попробуйте позже")
    else:
        bot.send_message(message.chat.id, "⛔️ Вы ввели не корректные данные")


def dep_trading(message):
    if message.text.isdigit():
        try:
            userid = str(message.chat.id)
            trading_dep = int(message.text)
            min_dep1 = 100
            if trading_dep >= min_dep1:
                connect = sqlite3.connect('bot.db')
                q = connect.cursor()
                q.execute(f"update info_deposit set deposit_to_traiding = deposit_to_traiding + '{trading_dep}' where id = '{userid}'")
                q.execute(f"update profile_info set balance = balance - '{trading_dep}' where id = '{userid}'")
                connect.commit()
                row = q.execute("SELECT * FROM info_partner where id is " + str(message.chat.id)).fetchone()
                q.close()
                if row is None:
                    bot.send_message(message.chat.id, f"Было успешно инвестировано {trading_dep}₽ в трейдинг", reply_markup=keyboard.main_menu)
                else:
                    bot.send_message(message.chat.id, f"Было успешно инвестировано {trading_dep}₽ в трейдинг", reply_markup=keyboard.partner_menu)
                    
            
            else:
                new_dep1 = bot.send_message(message.chat.id, f"Минимальная сумма депозита {min_dep1}")
                bot.clear_step_handler_by_chat_id(message.chat.id)
                bot.register_next_step_handler(new_dep1, dep_trading)
        except Exception as e:
            bot.send_message(config.error_chat, "!!!Ошибка!!!\n"\
                f"{e}")
            bot.send_message(message.chat.id, "Ошибка, попробуйте позже")
    
    else:
        bot.send_message(message.chat.id, "⛔️ Вы ввели не корректные данные")



def withdraw_qiwi(message):
    if message.text.isdigit():
        userid = str(message.chat.id)
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute("SELECT balance FROM profile_info where id is " + userid)
        balik = q.fetchone()[0]
        q.close()
        sum = int(message.text)
        if sum >= 100 and sum <= int(balik):
            send = bot.send_message(message.chat.id, "Введите реквизиты QIWI кошелька в формате +79062541562")
            bot.clear_step_handler_by_chat_id(message.chat.id)
            bot.register_next_step_handler(send, output_num, sum)
        else:
            new_send = bot.send_message(message.chat.id, "Введите коректную сумму для вывода")
            bot.clear_step_handler_by_chat_id(message.chat.id)
            bot.register_next_step_handler(new_send, withdraw_qiwi)
    else:
        bot.send_message(message.chat.id, "⛔️ Вы ввели не корректные данные для вывода. Закрываю вывод")



def withdraw_card(message):
    if message.text.isdigit():
        userid = str(message.chat.id)
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute("SELECT balance FROM profile_info where id is " + userid)
        balik = q.fetchone()[0]
        q.close()
        sum1 = int(message.text)
        if sum1 >= 100 and sum1 <= int(balik):
            send = bot.send_message(message.chat.id, "Введите номер своей карты")
            bot.clear_step_handler_by_chat_id(message.chat.id)
            bot.register_next_step_handler(send, output_num1, sum1)
        else:
            new_send = bot.send_message(message.chat.id, "Введите коректную сумму для вывода")
            bot.clear_step_handler_by_chat_id(message.chat.id)
            bot.register_next_step_handler(new_send, withdraw_card)
    else:
        bot.send_message(message.chat.id, "⛔️ Вы ввели не корректные данные для вывода. Закрываю вывод")

def withdraw_btc(message):
    if message.text.isdigit():
        userid = str(message.chat.id)
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute("SELECT balance FROM profile_info where id is " + userid)
        balik = q.fetchone()[0]
        q.close()
        sum2 = int(message.text)
        if sum2 >= 500 and sum2 <= int(balik):
            send = bot.send_message(message.chat.id, "Введите адрес своего btc кошелька")
            bot.clear_step_handler_by_chat_id(message.chat.id)
            bot.register_next_step_handler(send, output_num2, sum2)
        else:
            new_send = bot.send_message(message.chat.id, "Введите коректную сумму для вывода")
            bot.clear_step_handler_by_chat_id(message.chat.id)
            bot.register_next_step_handler(new_send, withdraw_btc)
    else:
        bot.send_message(message.chat.id, "⛔️ Вы ввели не корректные данные для вывода. Закрываю вывод")


def withdraw_eth(message):
    if message.text.isdigit():
        userid = str(message.chat.id)
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        q.execute("SELECT balance FROM profile_info where id is " + userid)
        balik = q.fetchone()[0]
        q.close()
        sum3 = int(message.text)
        if sum3 >= 500 and sum3 <= int(balik):
            send = bot.send_message(message.chat.id, "Введите адрес своего eth кошелька")
            bot.clear_step_handler_by_chat_id(message.chat.id)
            bot.register_next_step_handler(send, output_num3, sum3)
        else:
            new_send = bot.send_message(message.chat.id, "Введите коректную сумму для вывода")
            bot.clear_step_handler_by_chat_id(message.chat.id)
            bot.register_next_step_handler(new_send, withdraw_eth)
    else:
        bot.send_message(message.chat.id, "⛔️ Вы ввели не корректные данные для вывода. Закрываю вывод")


def output_num(message, sum):
    try:
        userid = str(message.chat.id)
        user_name = message.chat.username
        name = message.chat.first_name
        now = datetime.now()
        now_date = str(str(now)[:16])
        num = message.text
        zayavka = random.randint(1,10000000)
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        row = q.execute('SELECT * FROM info_vuvod WHERE chat_id IS ' + str(userid)).fetchone()
        q.execute("INSERT INTO info_vuvod (id, chat_id, summ, requisites) VALUES ('%s', '%s', '%s', '%s')"%(zayavka, userid, sum, num))    
        q.execute("INSERT INTO trans (zayavka, data1, summ) VALUES ('%s', '%s', '%s')"%(zayavka, now_date, sum))
        connect.commit()
        usr = bot.get_chat_member(message.chat.id, message.from_user.id)

        q.execute("SELECT balance FROM profile_info where id is " + userid)
        balik = q.fetchone()[0]
        q.execute(f"update profile_info set balance = balance - '{sum}' where id = '{userid}'")
        connect.commit()
        key = types.InlineKeyboardMarkup(row_width=2)
        done = types.InlineKeyboardButton("Выплачено", callback_data="done1_{}".format(zayavka))
        key.row(done)

        if not usr.user.username:
            bot.send_message(config.vuvod, f"Вывод от: {name}\n"\
                f"Чат айди пользователя: {userid}\n"\
                    f"Сумма на вывод: {sum}\n"\
                        f"Реквизиты киви: {num}", reply_markup=key)
            bot.send_message(message.chat.id, f"Заявка №{zayavka} на вывод успешно сформирована \n"\
                f"Сумма: {sum}\n"\
                    f"Реквизиты: {num}\n")

        else:
            bot.send_message(config.vuvod, f"Вывод от: @{user_name}\n"\
                f"Чат айди пользователя: {userid}\n"\
                    f"Сумма на вывод: {sum}\n"\
                        f"Реквизиты киви: {num}", reply_markup=key)
            bot.send_message(message.chat.id, f"Заявка №{zayavka} на вывод успешно сформирована \n"\
                f"Сумма: {sum}\n"\
                    f"Реквизиты: {num}\n")
    
    except Exception as e:
        bot.send_message(config.error_chat, "!!!Ошибка!!!\n"\
            f"{e}")
        bot.send_message(message.chat.id, "Ошибка, попробуйте позже")


def output_num1(message, sum1):
    try:
        userid = str(message.chat.id)
        user_name = message.chat.username
        name = message.chat.first_name
        num = message.text
        now = datetime.now()
        now_date = str(str(now)[:16])
        zayavka = random.randint(1,10000000)
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        row = q.execute('SELECT * FROM info_vuvod WHERE chat_id IS ' + str(userid)).fetchone()
        q.execute("INSERT INTO info_vuvod (id, chat_id, summ, requisites) VALUES ('%s', '%s', '%s', '%s')"%(zayavka, userid, sum1, num))        
        q.execute("INSERT INTO trans (zayavka, data1, summ) VALUES ('%s', '%s', '%s')"%(zayavka, now_date, sum1))
        connect.commit()
        usr = bot.get_chat_member(message.chat.id, message.from_user.id)

        q.execute("SELECT balance FROM profile_info where id is " + userid)
        balik = q.fetchone()[0]
        q.execute(f"update profile_info set balance = balance - '{sum1}' where id = '{userid}'")
        connect.commit()
        key = types.InlineKeyboardMarkup(row_width=2)
        done = types.InlineKeyboardButton("Выплачено", callback_data="done1_{}".format(zayavka))
        key.row(done)

        if not usr.user.username:
            bot.send_message(config.vuvod, f"Вывод от: {name}\n"\
                f"Чат айди пользователя: {userid}\n"\
                    f"Сумма на вывод: {sum1}\n"\
                        f"Реквизиты карты: {num}", reply_markup=key)
            
            bot.send_message(message.chat.id, f"Заявка №{zayavka} на вывод успешно сформирована \n"\
                f"Сумма: {sum1}\n"\
                    f"Реквизиты: {num}\n")

        else:
            bot.send_message(config.vuvod, f"Вывод от: @{user_name}\n"\
                f"Чат айди пользователя: {userid}\n"\
                    f"Сумма на вывод: {sum1}\n"\
                        f"Реквизиты карты: {num}", reply_markup=key)
            bot.send_message(message.chat.id, f"Заявка №{zayavka} на вывод успешно сформирована \n"\
                f"Сумма: {sum1}\n"\
                    f"Реквизиты: {num}\n")
    
    except Exception as e:
        bot.send_message(config.error_chat, "!!!Ошибка!!!\n"\
            f"{e}")
        bot.send_message(message.chat.id, "Ошибка, попробуйте позже")



def output_num2(message, sum2):
    try:
        userid = str(message.chat.id)
        user_name = message.chat.username
        name = message.chat.first_name
        num = message.text
        now = datetime.now()
        now_date = str(str(now)[:16])
        zayavka = random.randint(1,10000000)
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        row = q.execute('SELECT * FROM info_vuvod WHERE chat_id IS ' + str(userid)).fetchone()
        q.execute("INSERT INTO info_vuvod (id, chat_id, summ, requisites) VALUES ('%s', '%s', '%s', '%s')"%(zayavka, userid, sum2, num))
        q.execute("INSERT INTO trans (zayavka, data1, summ) VALUES ('%s', '%s', '%s')"%(zayavka, now_date, sum2))
        connect.commit()
        usr = bot.get_chat_member(message.chat.id, message.from_user.id)
            

        q.execute("SELECT balance FROM profile_info where id is " + userid)
        balik = q.fetchone()[0]
        q.execute(f"update profile_info set balance = balance - '{sum2}' where id = '{userid}'")
        connect.commit()
        key = types.InlineKeyboardMarkup(row_width=2)
        done = types.InlineKeyboardButton("Выплачено", callback_data="done1_{}".format(zayavka))
        key.row(done)

        if not usr.user.username:
            bot.send_message(config.vuvod, f"Вывод от: {name}\n"\
                f"Чат айди пользователя: {userid}\n"\
                    f"Сумма на вывод: {sum2}\n"\
                        f"Реквизиты кошелька: {num}", reply_markup=key)
            bot.send_message(message.chat.id, f"Заявка №{zayavka} на вывод успешно сформирована \n"\
                f"Сумма: {sum2}\n"\
                    f"Реквизиты: {num}\n")

        else:
            bot.send_message(config.vuvod, f"Вывод от: @{user_name}\n"\
                f"Чат айди пользователя: {userid}\n"\
                    f"Сумма на вывод: {sum2}\n"\
                        f"Реквизиты кошелька: {num}", reply_markup=key)
            bot.send_message(message.chat.id, f"Заявка №{zayavka} на вывод успешно сформирована \n"\
                f"Сумма: {sum2}\n"\
                    f"Реквизиты: {num}\n")
    
    except Exception as e:
        bot.send_message(config.error_chat, "!!!Ошибка!!!\n"\
            f"{e}")
        bot.send_message(message.chat.id, "Ошибка, попробуйте позже")


def output_num3(message, sum3):
    try:
        userid = str(message.chat.id)
        user_name = message.chat.username
        name = message.chat.first_name
        num = message.text
        now = datetime.now()
        now_date = str(str(now)[:16])
        zayavka = random.randint(1,10000000)
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        row = q.execute('SELECT * FROM info_vuvod WHERE chat_id IS ' + str(userid)).fetchone()
        q.execute("INSERT INTO info_vuvod (id, chat_id, summ, requisites) VALUES ('%s', '%s', '%s', '%s')"%(zayavka, userid, sum3, num))
        q.execute("INSERT INTO trans (zayavka, data1, summ) VALUES ('%s', '%s', '%s')"%(zayavka, now_date, sum3))
        connect.commit()
        usr = bot.get_chat_member(message.chat.id, message.from_user.id)
        
        q.execute("SELECT balance FROM profile_info where id is " + userid)
        balik = q.fetchone()[0]
        q.execute(f"update profile_info set balance = balance - '{sum3}' where id = '{userid}'")
        connect.commit()
        key = types.InlineKeyboardMarkup(row_width=2)
        done = types.InlineKeyboardButton("Выплачено", callback_data="done1_{}".format(zayavka))
        key.row(done)

        if not usr.user.username:
            bot.send_message(config.vuvod, f"Вывод от: {name}\n"\
                f"Чат айди пользователя: {userid}\n"\
                    f"Сумма на вывод: {sum3}\n"\
                        f"Реквизиты кошелька: {num}", reply_markup=key)
            bot.send_message(message.chat.id, f"Заявка №{zayavka} на вывод успешно сформирована \n"\
                f"Сумма: {sum3}\n"\
                    f"Реквизиты: {num}\n")

        else:
            bot.send_message(config.vuvod, f"Вывод от: @{user_name}\n"\
                f"Чат айди пользователя: {userid}\n"\
                    f"Сумма на вывод: {sum3}\n"\
                        f"Реквизиты кошелька: {num}", reply_markup=key)
            bot.send_message(message.chat.id, f"Заявка №{zayavka} на вывод успешно сформирована \n"\
                f"Сумма: {sum3}\n"\
                    f"Реквизиты: {num}\n")
    
    except Exception as e:
        bot.send_message(config.error_chat, "!!!Ошибка!!!\n"\
            f"{e}")
        bot.send_message(message.chat.id, "Ошибка, попробуйте позже")


def register_partner(message):
    user_id = message.chat.id
    name  = message.chat.first_name
    if "https" in message.text or "http" in message.text:
        link = message.text
        request = types.InlineKeyboardMarkup()
        confirm = types.InlineKeyboardButton("Одобрить заявка", callback_data="reqconf_{}_{}".format(user_id, name))
        cenc_conf = types.InlineKeyboardButton("Отменить заявку", callback_data="qeccenc_{}_{}".format(user_id,name))
        request.row(confirm, cenc_conf)


        bot.send_message(message.chat.id, "Ваша заявка на партнерство успешно сформирована\nОжидайте ответа от администрации")
        bot.send_message(config.vuvod, f"Завяка на партнерство от {name}\n"\
            f"Ссылка на ресурс: {link}",disable_web_page_preview=True, parse_mode="html", reply_markup=request)
    else:
        bot.send_message(message.chat.id, "Введите ссылку!")


def count_main(message):
    inv = message.text
    if inv.isdigit():
        inv = int(inv)
        day = inv * 0.05
        month = day * 30
        year = month * 12
        bot.send_message(message.chat.id, "В данном разделе мы рассчитали вашу прибыль от суммы инвестиции:\n\n"\
            f"💵 Ваша инвестиция: {inv} ₽\n"\
                f"➕ Прибыль в сутки: {day} ₽\n"\
                    f"➕ Прибыль в месяц: {month} ₽\n"\
                        f"➕ Прибыль в год: {year} ₽\n\n"\
                            "<b>Текущая процентная ставка: 5 % в день</b>", parse_mode='html')
    else:
        bot.send_message(message.chat.id, "⛔️ Вы не ввели данные для расчета. Закрываю расчет")

def count_trade(message):
    inv = message.text
    if inv.isdigit():
        inv = int(inv)
        percent = random.randint(1,15)
        inf = percent
        percent = percent / 100
        day = int(inv * percent)
        month = int(day * 30)
        year = int(month * 12)
        bot.send_message(message.chat.id, "В данном разделе мы рассчитали вашу прибыль от суммы инвестиции:\n\n"\
            f"💵 Ваша инвестиция: {inv} ₽\n"\
                f"➕ Прибыль в сутки: {day} ₽\n"\
                    f"➕ Прибыль в месяц: {month} ₽\n"\
                        f"➕ Прибыль в год: {year} ₽\n\n"\
                            f"<b>Текущая процентная ставка: {inf}% в день</b>", parse_mode='html')
    else:
        bot.send_message(message.chat.id, "⛔️ Вы не ввели данные для расчета. Закрываю расчет")

def accmain(message):
    if message.text.isdigit():
        if int(message.text) <= 5:
            try:
                connect = sqlite3.connect('bot.db')
                q = connect.cursor()
                percent = int(message.text) / 100
                result = q.execute("SELECT id FROM info_deposit").fetchall()
                cnt = 0
                for i in result:
                    balik1 = q.execute("SELECT deposit_to_maining FROM info_deposit where id is " + str(i[0])).fetchone()[0]
                    if int(balik1) > 0:
                        balik1 = int(int(balik1) * percent)
                        q.execute(f"update profile_info set balance = balance + '{balik1}' where id = '{i[0]}'")
                        connect.commit()
                        cnt += 1
                        try:
                            bot.send_message(i[0], f"<b>Сегодня было начислено {message.text}% от вашего депозита в майнинг {balik1}₽</b>", parse_mode='html')
                        except Exception as e:
                            bot.send_message(config.error_chat, "!!!Ошибка!!!\n"\
                                f"{e}")
                            bot.send_message(message.chat.id, "Произошла ошибка в отправке уведомления об начислению")
                        time.sleep(0.3)

                bot.send_message(message.chat.id, f"<b>Начисления прошло успешно</b>\n\n{cnt} человек получило начисления в размере {message.text}% от суммы инвестиции",parse_mode='html')
            except Exception as e:
                bot.send_message(config.error_chat, "!!!Ошибка!!!\n"\
                    f"{e}")
                bot.send_message(message.chat.id, "Произошла ошибка")
                    
        else:
            bot.send_message(message.chat.id,"Слишком большой % начисления, максимально 5%\n"\
                "<b>Закриваю начисления</b>", parse_mode='html')
            
    else:
        bot.send_message(message.chat.id,"Введите число!, Закриваю начисления")

def acctraid(message):
    if message.text.isdigit():
        try:
            if int(message.text) <= 15:
                connect = sqlite3.connect('bot.db')
                q = connect.cursor()
                percent = int(message.text) / 100
                result = q.execute("SELECT id FROM info_deposit").fetchall()
                cnt = 0
                for i in result:
                    balik1 = q.execute("SELECT deposit_to_traiding FROM info_deposit where id is " + str(i[0])).fetchone()[0]
                    if int(balik1) > 0:
                        balik1 = int(int(balik1) * percent)
                        q.execute(f"update profile_info set balance = balance + '{balik1}' where id = '{i[0]}'")
                        connect.commit()
                        cnt += 1
                        try:
                            bot.send_message(i[0], f"<b>Сегодня было начислено {message.text}% от вашего депозита в трейдинг {balik1}₽</b>", parse_mode='html')
                        except Exception as e:
                            bot.send_message(config.error_chat, "!!!Ошибка!!!\n"\
                                f"{e}")
                            bot.send_message(message.chat.id, "Произошла ошибка в отправке уведомления об начислению")
                        time.sleep(0.3)

                bot.send_message(message.chat.id, f"<b>Начисления прошло успешно</b>\n\n{cnt} человек получило начисления в размере {message.text}% от суммы инвестиции",parse_mode='html')
                    
            else:
                bot.send_message(message.chat.id,"Слишком большой % начисления, максимально 15%\n"\
                    "<b>Закриваю начисления</b>", parse_mode='html')
        except Exception as e:
            bot.send_message(config.error_chat, "!!!Ошибка!!!\n"\
                f"{e}")
            bot.send_message(message.chat.id, "Произошла ошибка")
    else:
        bot.send_message(message.chat.id,"Введите число!, Закриваю начисления")

def reset_key(message):
    try:
        token = message.text
        connect = sqlite3.connect('bot.db')
        q = connect.cursor()
        key = q.execute("SELECT * FROM qiwi_key").fetchone()
        if key is None:
            q.execute("INSERT INTO qiwi_key(qiwi) VALUES ('%s')"%(token))
            connect.commit()
            bot.send_message(message.chat.id, "ключ установился успешно")
        else:
            q.execute("DELETE FROM qiwi_key")
            connect.commit()
            q.execute("INSERT INTO qiwi_key(qiwi) VALUES ('%s')"%(token))
            connect.commit()
            bot.send_message(message.chat.id, "ключ установился успешно")
    except Exception as e:
        bot.send_message(config.error_chat, "!!!Ошибка!!!\n"\
            f"{e}")
        bot.send_message(message.chat.id, "Ошибка, попробуйте позже")

while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        bot.send_message(config.error_chat, "!!!Ошибка 1266!!!\n"\
            f"{e}")
        time.sleep(15)
        



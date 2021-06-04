import telebot
from telebot import types


partner_menu = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
partner_menu.add("💸Инвестировать💸", "💼Кабинет партнера💼")
partner_menu.add("ℹ️Статистикаℹ️","📠Калькулятор📠")
partner_menu.add("👨‍💻Support👨‍💻")

main_menu = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
main_menu.add("💸Инвестировать💸", "🖥Личный кабинет🖥")
main_menu.add("ℹ️Статистикаℹ️","📠Калькулятор📠")
main_menu.add("👨‍💻Support👨‍💻")

main_menu_admin = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
main_menu_admin.add("💸Инвестировать💸", "🖥Личный кабинет🖥")
main_menu_admin.add("ℹ️Статистикаℹ️","📠Калькулятор📠")
main_menu_admin.add("👨‍💻Support👨‍💻")
main_menu_admin.add("🏦Общий банк🏦", "💲Сделать начисления💲")
main_menu_admin.add("🔈Запустить рассылку🔈")
main_menu_admin.add("⚙️Сделать backup⚙️", "🔧Установить p2p ключ🔧")


main_menu_admin2 = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
main_menu_admin2.add("💸Инвестировать💸", "💼Кабинет партнера💼")
main_menu_admin2.add("ℹ️Статистикаℹ️","📠Калькулятор📠")
main_menu_admin2.add("👨‍💻Support👨‍💻")
main_menu_admin2.add("🏦Общий банк🏦", "💲Сделать начисления💲")
main_menu_admin2.add("🔈Запустить рассылку🔈")
main_menu_admin2.add("⚙️Сделать backup⚙️", "🔧Установить p2p ключ🔧")


start_confirm = types.InlineKeyboardMarkup()
agree = types.InlineKeyboardButton("C условиями ознакомлен✅", callback_data='agrees')
start_confirm.row(agree)


minimum_babok = types.InlineKeyboardMarkup()
top_up_balnce = types.InlineKeyboardButton("Пополнить баланс", callback_data="top_up")
minimum_babok.row(top_up_balnce)

spam = types.InlineKeyboardMarkup()
spam_text = types.InlineKeyboardButton("💬Спам текстом💬", callback_data="text")
spam_pic = types.InlineKeyboardButton("🖼Спам с картинкой🖼", callback_data="pics")
cancel_spam = types.InlineKeyboardButton("🙅Отмена рассылки🙅", callback_data="stop_spam")
spam.row(spam_text, spam_pic)
spam.row(cancel_spam)


invest_button = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
invest_button.add("⚙️Майнинг⚙️", "📊Трейдинг📊")
invest_button.add("🔙В главное меню🔙")

maining_button = types.InlineKeyboardMarkup()
main_invest = types.InlineKeyboardButton("Внести депозит", callback_data="main_invest")
main_info = types.InlineKeyboardButton("Подробней", url="https://telegra.ph/Vklady-v-majning-sektor-05-12")
maining_button.row(main_invest, main_info)

traid_button = types.InlineKeyboardMarkup()
traid_invest = types.InlineKeyboardButton("Внести депозит", callback_data="trade_invest")
traid_info = types.InlineKeyboardButton("Подробней", url="https://telegra.ph/Vklady-v-rynochnyj-depozit-05-12")
traid_button.row(traid_invest, traid_info)


payment_button = types.InlineKeyboardMarkup()
card = types.InlineKeyboardButton("💳Карта", callback_data="card") 
qiwi = types.InlineKeyboardButton("🥝Qiwi", callback_data="qiwi")
btc = types.InlineKeyboardButton('💲Bitcoin', callback_data="btc")
back_to_account = types.InlineKeyboardButton("Назад", callback_data="back")
payment_button.row(card)
payment_button.row(qiwi)
payment_button.row(btc)
payment_button.row(back_to_account)


withdraw_button = types.InlineKeyboardMarkup()
qiwi1 = types.InlineKeyboardButton("Qiwi", callback_data="qiwi1")
card1 = types.InlineKeyboardButton("Карта", callback_data="card1")
btc1 = types.InlineKeyboardButton("BTC", callback_data="btc1")
eth = types.InlineKeyboardButton("ETH", callback_data="eth")
withdraw_button.row(qiwi1,card1)
withdraw_button.row(btc1, eth)
withdraw_button.row(back_to_account)

back_to_payment = types.InlineKeyboardMarkup()
but1 = types.InlineKeyboardButton("Сменить тип пополнений", callback_data = "reset_payment")
back_to_payment.row(but1)


withdraw_partner = types.InlineKeyboardMarkup()
back_to_partner = types.InlineKeyboardButton("Назад", callback_data="backpart")
withdraw_partner.row(qiwi1,card1)
withdraw_partner.row(btc1, eth)
withdraw_partner.row(back_to_partner)

profile_partner = types.InlineKeyboardMarkup()
withdraw = types.InlineKeyboardButton("Заказать вывод", callback_data="withdrawpart")
profile_partner.row(withdraw)

calculate = types.InlineKeyboardMarkup()
calculate1 = types.InlineKeyboardButton("Майнинг", callback_data="calc1")
calculate2 = types.InlineKeyboardButton("Трейдинг", callback_data="calc2")
calculate.row(calculate1, calculate2)

accruals = types.InlineKeyboardMarkup()
accruals.row(types.InlineKeyboardButton("Майнинг", callback_data="accmain"), types.InlineKeyboardButton("Трейдинг", callback_data="acctraid"))







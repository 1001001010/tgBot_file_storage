from aiogram import types 

import base as db

menu = types.InlineKeyboardMarkup()
btn1 = types.InlineKeyboardButton(
    text = 'Файлы',
    callback_data = 'files'
)
btn2 = types.InlineKeyboardButton(
    text = 'Новый файл',
    callback_data = 'new_file'
)
menu.add(btn1, btn2)

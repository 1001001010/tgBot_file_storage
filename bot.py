from aiogram import types, executor, Dispatcher, Bot
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
# MODULES

import base as db
import keyboards as key
# FILES

settings =  {
    'token': '', # TOKEN
    'name': ''
}

storage = MemoryStorage()
bot = Bot(settings['token'])
dp = Dispatcher(bot, storage=storage)

class newfiles(StatesGroup):
    title = State()
    file = State()

class newcategory(StatesGroup):
    title = State()

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    _Check = await db.checkUser(user_id = message.from_user.id)
    if _Check == 1:
        await bot.send_message(message.from_user.id, f'Меню:', reply_markup=key.menu)
    else:
        await db.insertUser(user_id=message.from_user.id)
        await bot.send_message(message.from_user.id, f'Меню: ', reply_markup=key.menu)

@dp.callback_query_handler()
async def call_handler(call: types.CallbackQuery):
    if call.data == 'files':
        categories = await db.genCategories(call.from_user.id)
        if categories != 0:
            await bot.send_message(call.from_user.id, f'Категории:', reply_markup=categories)
        else:
            await bot.send_message(call.from_user.id, f'Категорий нету!')
    if call.data == 'new_file':
        await bot.send_message(call.from_user.id, f'Введите название для проекта')
        await newfiles.title.set()

    if call.data == 'new_categor':
        await bot.send_message(call.from_user.id, f'Введите название категории')
        await newcategory.title.set()

    if call.data == 'none_categor':
        files = await db.genNonCategoryFiles(user_id = call.from_user.id)
        print(files)
        keyboard = types.InlineKeyboardMarkup()
        for i in files:
            keyboard.add(
                types.InlineKeyboardButton(text = f'{i[3]}', callback_data=f'sendfile|{i[0]}')
            )
        await bot.send_message(call.from_user.id, 'Файлы без категории: ', reply_markup=keyboard)

    if 'sendfile' in call.data:
        file_id = call.data.split('|')[1]
        file = await db.getFile(file_id)
        keyboard = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton(text='Сменить категорию', callback_data=f'swap|{file_id}')
        keyboard.add(btn1)
        await bot.send_document(call.from_user.id, file[2], caption=f'Название проекта: {file[3]}', reply_markup=keyboard)

    if 'swap' in call.data:
        file_id = call.data.split('|')[1]
        categories = await db.getCategories(user_id = call.from_user.id)
        print(categories)
        keyboard = types.InlineKeyboardMarkup()
        for i in categories:
            keyboard.add(types.InlineKeyboardButton(text=i[2], callback_data=f'to|{file_id}|{i[0]}'))
        await bot.send_message(call.from_user.id, f'Выберите категорию: ', reply_markup=keyboard)

    if 'to' in call.data:
        file_id = call.data.split('|')[1]
        category = call.data.split('|')[2]
        await db.changeCategory(file_id, category)
        await bot.send_message(call.from_user.id, f'Вы сменили категорию у файла!')

    if 'category' in call.data:
        category_id = call.data.split('_')[1]
        files = await db.getFileswithCategory(user_id = call.from_user.id, category=category_id)
        keyboard = types.InlineKeyboardMarkup()
        for i in files:
            keyboard.add(types.InlineKeyboardButton(text=f'{i[3]}', callback_data=f'sendfile|{i[0]}'))
        await bot.send_message(call.from_user.id, f'Категория:', reply_markup=keyboard)


@dp.message_handler(state = newcategory.title)
async def state_newcategory(message: types.Message, state: FSMContext):
    await state.update_data(title = message.text)
    await db.newCategory(user_id=message.from_user.id, title=message.text)
    await bot.send_message(message.from_user.id, f'Категория создана!')
    await state.finish()

@dp.message_handler(state = newfiles.title)
async def state_newfiles(message: types.Message, state: FSMContext):
    await state.update_data(title = message.text)
    await bot.send_message(message.from_user.id, f'Отправьте файлы: ')
    await newfiles.file.set()

@dp.message_handler(content_types=[types.ContentType.DOCUMENT], state = newfiles.file)
async def state_files(message: types.Message, state: FSMContext):
    file_id = message.document.file_id
    data = await state.get_data()
    title = data['title']
    await db.new_file(user_id = message.from_user.id, title = title, file_id = file_id)
    await state.finish()
    await bot.send_message(message.from_user.id, f'Вы добавили новый файл!')


executor.start_polling(dp)

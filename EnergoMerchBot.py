import asyncio
import os
import logging
import sys

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from imports.utils import *
from imports.config import *
from imports.NameSystem import NameSystem

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
folder = WORK_FOLDER
data_frame = None
find_trie = Trie()
GNS = NameSystem()  # Global Name System



def update_data_frame(start: bool = False) -> None:
    """Read data from base file and store it to the trie and to the pandas dataFrame"""

    def log_and_exit(message: str) -> None:
        logging.log(logging.CRITICAL, message)
        if start:
            sys.exit(message)

    global data_frame
    global find_trie
    global GNS
    files = []
    new_find_trie = Trie()
    root = None
    for root, dirs, files in os.walk(folder):
        break
    for file in files:
        if file.endswith('.xlsx'):
            try:
                data_frame = get_data_from_file(os.path.join(root, file), new_find_trie, GNS)
                find_trie = new_find_trie
            except OSError:
                log_and_exit('Base file not accessible!!!')
            except KeyError:
                log_and_exit('Incorrect base file structure')
            break


async def on_bot_start_up(dispatcher: Dispatcher) -> None:
    asyncio.create_task(background_job_refresh_data())


async def background_job_refresh_data() -> None:
    while True:
        await asyncio.sleep(WORKER_DELAY_IN_SECONDS)
        update_data_frame()


@dp.message_handler(commands=['start'])
async def show_start(message: types.Message):
    new_first_markup = create_standard_markup('', find_trie.get_children(''))
    await message.answer(text='Выберите свою территорию или пришлите ее название', reply_markup=new_first_markup)


def create_button(text: str, data, button_prefix=BUTTON_PREFIX):
    button = InlineKeyboardButton(text=text, callback_data=f'{button_prefix}{data}')
    return button


def create_reply_markup(data: str) -> Any:
    """Return an inline keyboard markup with one button"""
    reply_markup = InlineKeyboardMarkup()
    button = create_button('Повторить последний запрос', data)
    reply_markup.add(button)
    return reply_markup


def create_standard_markup(query: str, children) -> Any:
    markup = InlineKeyboardMarkup(row_width=3)
    for i in range(0, len(children)):
        element = children[i]
        button = InlineKeyboardButton(text=element, callback_data=f'{BUTTON_PREFIX}{query}_{GNS.get_forward(element)}')
        if i % 3 == 0:
            markup.add(button)
        else:
            markup.insert(button)
    return markup


@dp.callback_query_handler()
async def process_callbacks(callback_query: types.CallbackQuery):
    """Handling a response to a button click"""
    await callback_query.answer(callback_query.id)
    if not callback_query.data.startswith(BUTTON_PREFIX):
        await bot.send_message(callback_query.from_user.id,
                               text='Устаревшая версия кнопок, сотрите историю и начните заново')
        return
    query = callback_query.data[len(BUTTON_PREFIX):].strip('_')
    children = find_trie.get_children(GNS.reverse_replace(query))
    if len(children) > 0:
        new_markup = create_standard_markup(query, children)
        await bot.send_message(callback_query.from_user.id, text=GNS.reverse_replace(query), reply_markup=new_markup)
    else:
        reply_markup = create_reply_markup(query)
        territory_index = find_trie.get_index(GNS.reverse_replace(query))
        data_row_list = data_frame.loc[territory_index, :].values.tolist()[1:]
        result = convert_to_string(GNS.reverse_replace(query), data_row_list)
        await bot.send_message(callback_query.from_user.id, text=result, parse_mode='HTML', reply_markup=reply_markup)


@dp.message_handler()
async def echo(message: types.Message):
    """Handling a response to a text query"""
    reply_markup = create_reply_markup(GNS.forward_replace(message.text))
    territory_index = find_trie.get_index(message.text)
    data_row_list = data_frame.loc[territory_index, :].values.tolist()[1:]
    result = convert_to_string('', data_row_list)
    await message.answer(text=result, parse_mode='HTML', reply_markup=reply_markup)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S')
    update_data_frame(start=True)
    executor.start_polling(dp, skip_updates=True, on_startup=on_bot_start_up)

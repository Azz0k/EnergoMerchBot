import asyncio
import os
import logging
import sys

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from imports.utils import *
from imports.config import *
from imports.TwoWayDict import TwoWayDict
from imports.Support import Support

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
support = Support()


async def on_bot_start_up(dispatcher: Dispatcher) -> None:
    asyncio.create_task(background_job_refresh_data())


async def background_job_refresh_data() -> None:
    while True:
        await asyncio.sleep(WORKER_DELAY_IN_SECONDS)
        support.update_data_frame()


@dp.message_handler(commands=['start'])
async def show_start(message: types.Message):
    new_first_markup = support.create_standard_markup('')
    await message.answer(text='Выберите свою территорию или пришлите ее название', reply_markup=new_first_markup)


@dp.callback_query_handler()
async def process_callbacks(callback_query: types.CallbackQuery):
    """Handling a response to a button click"""
    await callback_query.answer(callback_query.id)
    if not callback_query.data.startswith(BUTTON_PREFIX):
        await bot.send_message(callback_query.from_user.id,
                               text='Устаревшая версия кнопок, сотрите историю и начните заново')
        return
    query = callback_query.data[len(BUTTON_PREFIX):].strip('_')
    children = support.get_children(query)
    if len(children) > 0:
        markup = support.create_standard_markup(query)
        text = support.replace_ids_with_names(query)
        await bot.send_message(callback_query.from_user.id, text=text, reply_markup=markup)
    else:
        text = support.get_answer(query)
        markup = support.create_reply_markup(query)
        await bot.send_message(callback_query.from_user.id, text=text, parse_mode='HTML', reply_markup=markup)


@dp.message_handler()
async def echo(message: types.Message):
    """Handling a response to a text query"""
    markup = InlineKeyboardMarkup()
    text = support.get_answer(message.text.strip())
    if text != NOT_FOUND_ANSWER:
        markup = support.create_reply_markup(message.text)
    await message.answer(text=text, parse_mode='HTML', reply_markup=markup)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S')
    support.update_data_frame(start=True)
    executor.start_polling(dp, skip_updates=True, on_startup=on_bot_start_up)

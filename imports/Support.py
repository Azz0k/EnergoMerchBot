import asyncio
import os
import logging
import sys

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from imports.utils import *
from imports.config import *
from imports.TwoWayDict import TwoWayDict


class Support:

    def __init__(self):
        self.find_trie = Trie()
        self.data_frame = None
        self.name_vs_id = TwoWayDict()

    def get_data_from_file(self, file_name: str) -> Any:
        df = pd.read_excel(file_name)
        trie = Trie()
        del df['Unnamed: 0']
        del df['Unnamed: 1']
        del df['DSM']
        del df['SV']
        for i in range(1, len(df['МС'])):
            self.name_vs_id.split_string_and_add(df['МС'][i].strip())
            trie.insert(df['МС'][i].strip(), i)
        self.data_frame = df
        return trie

    def update_data_frame(self, start: bool = False) -> None:
        """Read data from base file and store it to the trie and to the pandas dataFrame"""

        def log_and_exit(message: str) -> None:
            logging.log(logging.CRITICAL, message)
            if start:
                sys.exit(message)

        files = []
        root = None
        for root, dirs, files in os.walk(WORK_FOLDER):
            break
        for file in files:
            if file.endswith('.xlsx'):
                try:
                    self.find_trie = self.get_data_from_file(os.path.join(root, file))
                except OSError:
                    log_and_exit('Base file not accessible!!!')
                except KeyError:
                    log_and_exit('Incorrect base file structure')
                break

    def create_reply_markup(self, data: str) -> Any:
        """Return an inline keyboard markup with one button"""
        reply_markup = InlineKeyboardMarkup()
        if data[0:1].isalpha():
            data = self.name_vs_id.replace_names_with_ids(data)
        button = InlineKeyboardButton(text='Повторить последний запрос', callback_data=f'{BUTTON_PREFIX}{data}')
        reply_markup.add(button)
        return reply_markup

    def create_standard_markup(self, query: str) -> Any:
        markup = InlineKeyboardMarkup(row_width=3)
        callback_id = query
        if query[0:1].isdigit():
            callback_id = self.name_vs_id.replace_ids_with_names(query)
        children = self.find_trie.get_children(callback_id)
        for i in range(0, len(children)):
            element = children[i]
            button = InlineKeyboardButton(text=element,
                                          callback_data=f'{BUTTON_PREFIX}{query}_{self.name_vs_id.get_id_from_name(element)}')
            if i % 3 == 0:
                markup.add(button)
            else:
                markup.insert(button)
        return markup

    def get_children(self, query: str) -> Any:
        return self.find_trie.get_children(self.name_vs_id.replace_ids_with_names(query))

    def get_index(self, query: str) -> Any:
        return self.find_trie.get_index(self.name_vs_id.replace_ids_with_names(query))

    def get_answer(self, query: str) -> Any:
        territory_name = query
        if query[0:1].isalpha():
            territory_index = self.find_trie.get_index(query)
            if territory_index == -1:
                return NOT_FOUND_ANSWER
        else:
            territory_index = self.find_trie.get_index(self.name_vs_id.replace_ids_with_names(query))
            territory_name = self.name_vs_id.replace_ids_with_names(query)
        data_row_list = self.data_frame.loc[territory_index, :].values.tolist()[1:]
        result = convert_to_string(territory_name, data_row_list)
        return result

    def replace_ids_with_names(self, query: str):
        return self.name_vs_id.replace_ids_with_names(query)

from typing import Any
import pandas as pd
from imports.Trie import Trie
from imports.NameSystem import NameSystem
import math


def convert_to_string(name, arg_list: list) -> str:
    arg_list = [0 if math.isnan(x) else x for x in arg_list]
    arg_list.append(name)
    result = """
<b>{24}</b>

<b>Кофе-{2:.0%}</b>
План-{0}
Факт-{1}
<b>Кондитерские изделия-{5:.0%}</b>
План-{3}
Факт-{4}
<b>Кулинария-{8:.0%}</b>
План-{6}
Факт-{7}
<b>Каши Быстров-{11:.0%}</b>
План-{9}
Факт-{10} 
<b>Какао Несквик-{14:.0%}</b>
План-{12}
Факт-{13}
<b>Готовые завтраки-{17:.0%}</b>
План-{15}
Факт-{16} 
<b>Детское питание-{20:.0%}</b>
План-{18}
Факт-{19}
<b>Корм для животных-{23:.0%}</b>
План-{21}
Факт-{22}
"""
    return result.format(*arg_list)


def test_convert_to_string():
    case = list(range(0, 24))
    res = convert_to_string(case)
    assert res == '<b>Кофе-200%</b>\nПлан-0\nФакт-1\n<b>Кондитерские ' \
                  'изделия-500%</b>\nПлан-3\nФакт-4\n<b>Кулинария-800%</b>\nПлан-6\nФакт-7\n<b>Каши ' \
                  'Быстров-1100%</b>\nПлан-9\nФакт-10 \n<b>Какао Несквик-1400%</b>\nПлан-12\nФакт-13\n<b>Готовые ' \
                  'завтраки-1700%</b>\nПлан-15\nФакт-16 \n<b>Детское питание-2000%</b>\nПлан-18\nФакт-19\n<b>Корм для ' \
                  'животных-2300%</b>\nПлан-21\nФакт-22\n'


def get_data_from_file(file_name: str, trie: Trie, global_name_system: NameSystem) -> Any:
    df = pd.read_excel(file_name)
    del df['Unnamed: 0']
    del df['Unnamed: 1']
    del df['DSM']
    del df['SV']
    for i in range(1, len(df['МС'])):
        global_name_system.add_string_to_ns(df['МС'][i].strip())
        trie.insert(df['МС'][i].strip(), i)
    return df


if __name__ == '__main__':
    test_convert_to_string()

import json, re
from os import getenv
from openai import OpenAI
import json

client = OpenAI()


chat_japanese_proficiency = "JLPT N2"
current_gpt_model = "gpt-3.5-turbo-0125"
rtk_kanji_obj = {}

hiragana_list = [
    'あ', 'い', 'う', 'え', 'お',
    'か', 'き', 'く', 'け', 'こ',
    'が', 'ぎ', 'ぐ', 'げ', 'ご',
    'さ', 'し', 'す', 'せ', 'そ',
    'ざ', 'じ', 'ず', 'ぜ', 'ぞ',
    'た', 'ち', 'つ', 'て', 'と',
    'だ', 'ぢ', 'づ', 'で', 'ど',
    'な', 'に', 'ぬ', 'ね', 'の',
    'は', 'ひ', 'ふ', 'へ', 'ほ',
    'ば', 'び', 'ぶ', 'べ', 'ぼ',
    'ぱ', 'ぴ', 'ぷ', 'ぺ', 'ぽ',
    'ま', 'み', 'む', 'め', 'も',
    'や', 'ゆ', 'よ',
    'ら', 'り', 'る', 'れ', 'ろ',
    'わ', 'を', 'ん',
]

katakana_list = [
    'ア', 'イ', 'ウ', 'エ', 'オ',
    'カ', 'キ', 'ク', 'ケ', 'コ',
    'ガ', 'ギ', 'グ', 'ゲ', 'ゴ',
    'サ', 'シ', 'ス', 'セ', 'ソ',
    'ザ', 'ジ', 'ズ', 'ゼ', 'ゾ',
    'タ', 'チ', 'ツ', 'テ', 'ト',
    'ダ', 'ヂ', 'ヅ', 'デ', 'ド',
    'ナ', 'ニ', 'ヌ', 'ネ', 'ノ',
    'ハ', 'ヒ', 'フ', 'ヘ', 'ホ',
    'バ', 'ビ', 'ブ', 'ベ', 'ボ',
    'パ', 'ピ', 'プ', 'ペ', 'ポ',
    'マ', 'ミ', 'ム', 'メ', 'モ',
    'ヤ', 'ユ', 'ヨ',
    'ラ', 'リ', 'ル', 'レ', 'ロ',
    'ワ', 'ヲ', 'ン',
]
other_characters_table = ["ゃ", "ゅ", "ょ", "っ", "ァ", "ィ", "ゥ", "ェ", "ォ", "ャ", "ュ", "ョ", "ッ", "ー", "。", "、", "？", "！", "「", "」", "・", "〜", "…", "（", "）", "：", "；", "［", "］", "＜", "＞", "＝", "＠", "＃", "＄", "％", "＆", "＊", "＋", "－", "／", "＼", "＾", "｜", "～", "＿", "＇", "＂", "｀", "｛", "｝", "＜", "＞", "＝", "＼", "｜", "＠", "＃", "＄", "％", "＾", "＆", "＊", "（", "）", "＿", "＋", "｀", "～", "｛", "｝", "［", "］", "：", "；", "＂", "＇", "｜", "＼", "＜", "＞", "？", "！", "。", "、", "・", "…", "ー", "゛", "゜", "ゝ", "ゞ"]


message_list = [
    {
      "role": "system",
      "content": f"I am a Japanese conversation bot designed to speak on a level similar to {chat_japanese_proficiency}.\n\nI will have basic conversation with the user.\nI will add a table at the end of the message containing the hiragana for every word used in my answer to the user, as well as the word itself, and the meaning of the word in the context of the conversation. This table will include ALL the words I use (no limits, the more words, the better), no matter how simple or complicated the words are. The table should be as long as possible, and contain EVERY SINGLE WORD I say in my main message"
    },
    {
      "role": "user",
      "content": ""
    },
    {
      "role": "assistant",
      "content": "今日は！元気ですか？何か話したいことがあれば遠慮なく言ってくださいね。\n\n| Word (Kanji) | Hiragana | Meaning |\n|--------------|----------|---------| \n| 今日は | こんにちは | Hello |\n| 元気 | げんき | Energy; health |\n| 何か | なにか | Something |\n| 話す | はなす | To speak |\n| 遠慮 | えんりょ | Hesitation; reservation |\n| 言って | いって | To say; To speak"
    }
  ]

def toggle_word_kanji_to_hiragana(word):
    with open('known_words.json', 'r') as file:
        known_words = json.load(file)


    if word in known_words:
        known_words.remove(word)
        status = False
    else:
        known_words.append(word)
        status = True

    with open('known_words.json', 'w') as file:
        json.dump(known_words, file)

    return status

def set_chat_japanese_proficiency(proficiency):
    global chat_japanese_proficiency
    chat_japanese_proficiency = proficiency

def set_current_rtk_level(level):
    global rtk_kanji_obj
    with open('kanji_list.json') as file:
        rtk_kanji_list = json.load(file)

    MAX_RTK_KANJI_NUMBER = level
    if MAX_RTK_KANJI_NUMBER > len(rtk_kanji_list):
        MAX_RTK_KANJI_NUMBER = len(rtk_kanji_list)
    rtk_kanji_list = rtk_kanji_list[:MAX_RTK_KANJI_NUMBER]
    rtk_kanji_obj = {obj["kanji"]: obj["rtk_order"] for obj in rtk_kanji_list}


def basic_message_formatting(machine_message):
    header_pattern = re.compile(r'\|\s*Word \(Kanji\)\s*\|\s*Hiragana\s*\|\s*Meaning.*\s*\|')
    header = header_pattern.search(machine_message)
    header = header.group() if header else None

    if header:
        machine_message = machine_message.split(header)
        original_message, original_table = machine_message[0].replace("\n", ""), machine_message[1]

        table = original_table.split("\n")
        table_elements = []
        for idx, row in enumerate(table):
            elements = [item.strip() for item in row.split("|") if item.strip()]
            if len(elements) == 3 and not len(elements[0].replace("-", "")) == 0:
                table_elements.append({"kanji": elements[0], "hiragana": elements[1], "meaning": elements[2], "index": idx, "contains_known_kanji":False})

        return original_message, original_table, table_elements
    print("No table found in message? :", machine_message)

def custom_assistant_formatting(machine_message, custom_elements=False, custom_table=False):
        original_message, _, table_elements = basic_message_formatting(machine_message)
        if custom_elements:
            table_elements = custom_table
            original_message = custom_elements["original"]

        original_message = re.sub(r'「.*?」', '', original_message).strip()

        REPLACE_LEFT = "`"
        REPLACE_RIGHT = "``---"

        known_rtk_kanji = []
        hiragana_only_message = original_message
        non_kanji_characters = original_message
        for element in table_elements:
            for individual_kanji in element["kanji"]:
                if is_know_rtk_kanji(individual_kanji):
                    element["contains_known_kanji"] = True
                    known_rtk_kanji.append(individual_kanji)
            non_kanji_characters = non_kanji_characters.replace(element["kanji"], f"{REPLACE_LEFT}{element['index']}{REPLACE_RIGHT}")
            hiragana_only_message = hiragana_only_message.replace(element["kanji"], element['hiragana'])

        # Order table elements by index key, remove duplicates
        table_elements_index = []
        new_table_elements = []
        for element in table_elements:
            if element["index"] not in table_elements_index:
                table_elements_index.append(element["index"])
                new_table_elements.append(element)
        table_elements = sorted(new_table_elements, key=lambda x: x["index"])

        with open('known_words.json', 'r') as file:
            known_words = json.load(file)

        known_rtk_kanji = list(set(known_rtk_kanji))

        separated_elements = []
        for element in non_kanji_characters.split(REPLACE_RIGHT):
            splited_element = element.split(REPLACE_LEFT)
            if REPLACE_LEFT not in element and len(splited_element) == 1:
                non_word_characters, index = element, None
            elif REPLACE_LEFT in element and len(splited_element) == 1:
                non_word_characters, index = None, splited_element[0]
            else:
                non_word_characters, index = splited_element
            index = int(index) if index else None

            if non_word_characters:
                word_object = {
                    "is_word": False,
                    "content": non_word_characters,
                    "kanji": None,
                    "hiragana": None,
                    "meaning": None,
                    "show_kanji": False,
                    "contains_known_kanji": False,
                    "known_kanji": []
                }
                separated_elements.append(word_object)
            if not index:
                continue

            idx = index - 1
            word_object = {
                "is_word": True,
                "content": idx,
                "kanji": table_elements[idx]["kanji"],
                "hiragana": table_elements[idx]["hiragana"],
                "meaning": table_elements[idx]["meaning"],
                "contains_known_kanji": table_elements[idx]["contains_known_kanji"],
                "show_kanji": table_elements[idx]["kanji"] in known_words,
                "known_kanji": [_kanji for _kanji in known_rtk_kanji if _kanji in table_elements[idx]["kanji"]]
            }
            separated_elements.append(word_object)

        output = {
            "original": original_message,
            "hiragana": hiragana_only_message,
            "non_kanji_characters": separated_elements,
            "table": table_elements,
            "known_rtk_kanji": list(set(known_rtk_kanji))
        }

        return output

def is_know_rtk_kanji(kanji):
    global rtk_kanji_obj

    if kanji in rtk_kanji_obj:
        return True
    return False

def trim_memory():
    global message_list

    if len(message_list) > 6:
        message_list = message_list[:3] + message_list[-4:]

def fix_incomplete_kanji_table(custom_elements):

    hiragana_message = custom_elements["hiragana"]
    original_table_elements = custom_elements["table"]
    global message_list
    undefined_kanji = []
    for character in hiragana_message:
        if character in hiragana_list or character in katakana_list or character in other_characters_table:
            continue
        else:
            undefined_kanji.append(character)

    if not undefined_kanji:
        return custom_elements
    response = send_api_message(f"the table you generated missed some kanji, return me a table only containing what was missing (the missing words contain these kanji: {', '.join(undefined_kanji)}).\n\n Here is a message transforming the known kanji to hiragana: {hiragana_message}\n\n The table should contain the words that still have kanji in them, following the prevous format. The hiragana message I just sent includes kanji that could be in the table already but you should include regardless. It there is a word that uses the same kanji, it should be added to the table too. Consider things like 思う and 思い, or 聞く and 聞き to be different words, just for the sake of the table. Also, include basic kanji like 何 too.")
    message_list = message_list[:-1]

    machine_message = response.choices[0].message.content


    _, _, new_table_elements = basic_message_formatting(machine_message)
    custom_table = []

    both_tables = original_table_elements + new_table_elements

    for idx, element in enumerate(both_tables):
        element["index"] = idx
        custom_table.append(element)
    message_properties = custom_assistant_formatting(machine_message, custom_elements=custom_elements, custom_table=custom_table)
    return message_properties

def set_gpt_model(model_name):
    global current_gpt_model
    current_gpt_model = model_name

def send_api_message(user_message):
    global message_list, current_gpt_model

    message_list.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
    model=current_gpt_model,
    messages=message_list,
    temperature=1,
    max_tokens=4096,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )

    return response


def send_user_message(user_message):
    response = send_api_message(user_message)

    machine_message = response.choices[0].message.content
    message_list.append({"role": "assistant", "content": machine_message})
    trim_memory()
    assistant_response = custom_assistant_formatting(machine_message)
    incomplete_kanji_fix = fix_incomplete_kanji_table(assistant_response)

    if incomplete_kanji_fix:
        return incomplete_kanji_fix

    return assistant_response

# Create new variables, like `chat_japanese_proficiency`, `rtk_kanji_obj` and `message_list`,
# to store the chat proficiency level and the kanji list,
# respectively and them being stored in a database so we can sort of create sessions
# Also a list of words you no longer want to be shown in hiragana
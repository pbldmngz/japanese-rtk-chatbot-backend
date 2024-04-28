from openai import OpenAI
from utils.settings import hiragana_list, katakana_list, other_characters_table
from utils.logic import basic_message_formatting, custom_assistant_formatting
from utils.database import UserConfigDB

client = OpenAI()


def trim_memory(username):
    db = UserConfigDB()
    user = db.get_user(username)
    message_list = user['message_log']
    if len(message_list) > 6:
        message_list = message_list[:3] + message_list[-4:]
        db.update_field(username, 'message_log', message_list)

def fix_incomplete_kanji_table(custom_elements, username):

    hiragana_message = custom_elements["hiragana"]
    original_table_elements = custom_elements["table"]

    undefined_kanji = []
    for character in hiragana_message:
        if character in hiragana_list or character in katakana_list or character in other_characters_table:
            continue
        else:
            undefined_kanji.append(character)

    if not undefined_kanji:
        return custom_elements
    response = send_api_message(f"the table you generated missed some kanji, return me a table only containing what was missing (the missing words contain these kanji: {', '.join(undefined_kanji)}).\n\n Here is a message transforming the known kanji to hiragana: {hiragana_message}\n\n The table should contain the words that still have kanji in them, following the prevous format. The hiragana message I just sent includes kanji that could be in the table already but you should include regardless. It there is a word that uses the same kanji, it should be added to the table too. Consider things like 思う and 思い, or 聞く and 聞き to be different words, just for the sake of the table. Also, include basic kanji like 何 too.")

    db = UserConfigDB()
    user = db.get_user(username)
    message_list = user['message_log']
    message_list = message_list[:-1]
    db.update_field(username, 'message_log', message_list)

    machine_message = response.choices[0].message.content


    _, _, new_table_elements = basic_message_formatting(machine_message)
    custom_table = []

    both_tables = original_table_elements + new_table_elements

    for idx, element in enumerate(both_tables):
        element["index"] = idx
        custom_table.append(element)
    message_properties = custom_assistant_formatting(machine_message, username, custom_elements=custom_elements, custom_table=custom_table)
    return message_properties

def send_api_message(user_message, username):
    db = UserConfigDB()
    user = db.get_user(username)
    message_list = user['message_log']
    current_gpt_model = user['gpt_model']

    message_list.append({"role": "user", "content": user_message})
    db.update_field(username, 'message_log', message_list)

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

def send_user_message(user_message, username):
    response = send_api_message(user_message, username)

    machine_message = response.choices[0].message.content

    db = UserConfigDB()
    user = db.get_user(username)
    message_list = user['message_log']
    message_list.append({"role": "assistant", "content": machine_message})
    db.update_field(username, 'message_log', message_list)
    trim_memory(username)
    assistant_response = custom_assistant_formatting(machine_message, username)
    incomplete_kanji_fix = fix_incomplete_kanji_table(assistant_response, username)

    if incomplete_kanji_fix:
        return incomplete_kanji_fix

    return assistant_response


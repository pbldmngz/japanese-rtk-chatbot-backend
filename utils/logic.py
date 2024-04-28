import re
from utils.settings import hiragana_list, katakana_list, other_characters_table, get_known_words, get_current_rtk_level
from utils.database import UserConfigDB


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

def custom_assistant_formatting(machine_message, username, custom_elements=False, custom_table=False):
        db = UserConfigDB()
        user = db.get_user(username)
        rtk_level = user['rtk_level']
        current_rtk_available = get_current_rtk_level(rtk_level)
        original_message, _, table_elements = basic_message_formatting(machine_message)
        if custom_elements:
            table_elements = custom_table
            original_message = custom_elements["original"]

        original_message = re.sub(r'「.*?」', '', original_message).strip()

        while original_message[0] in other_characters_table:
            original_message = original_message[1:]

        REPLACE_LEFT = "`"
        REPLACE_RIGHT = "``---"

        known_rtk_kanji = []
        hiragana_only_message = original_message
        non_kanji_characters = original_message
        for element in table_elements:
            for individual_kanji in element["kanji"]:
                if is_know_rtk_kanji(individual_kanji, current_rtk_available):
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

        known_words = get_known_words(username)

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
                    "known_kanji": [],
                    "contains_kanji": False
                }
                separated_elements.append(word_object)
            if not index:
                continue

            idx = index - 1

            contains_no_kanji_at_all = True
            found_kanji = []
            for el in table_elements[idx]["kanji"]:
                if not (el in hiragana_list + katakana_list + other_characters_table):
                    found_kanji.append(el)

            known_kanji = [_kanji for _kanji in known_rtk_kanji if _kanji in table_elements[idx]["kanji"]]
            unknown_kanji = [_kanji for _kanji in found_kanji if _kanji not in known_kanji]

            if found_kanji:
                contains_no_kanji_at_all = False

            word_object = {
                "is_word": True,
                "content": idx,
                "kanji": table_elements[idx]["kanji"],
                "hiragana": table_elements[idx]["hiragana"],
                "meaning": table_elements[idx]["meaning"],
                "contains_known_kanji": table_elements[idx]["contains_known_kanji"],
                "show_kanji": table_elements[idx]["kanji"] in known_words,
                "known_kanji": known_kanji,
                "unknown_kanji": unknown_kanji,
                "contains_no_kanji": contains_no_kanji_at_all
            }

            if "、" in [word_object["kanji"], word_object["hiragana"], word_object["meaning"]]:
                continue
            separated_elements.append(word_object)

        output = {
            "original": original_message,
            "hiragana": hiragana_only_message,
            "non_kanji_characters": separated_elements,
            "table": table_elements,
            "known_rtk_kanji": list(set(known_rtk_kanji))
        }

        return output

def is_know_rtk_kanji(kanji, known_kanji:dict):
    if kanji in known_kanji:
        return True
    return False
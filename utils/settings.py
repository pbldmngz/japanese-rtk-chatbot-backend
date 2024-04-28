import json
from utils.database import UserConfigDB

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
other_characters_table = [" ","ゃ", "ゅ", "ょ", "っ", "ァ", "ィ", "ゥ", "ェ", "ォ", "ャ", "ュ", "ョ", "ッ", "ー", "。", "、", "？", "？", "！", "！", "「", "」", "・", "〜", "…", "（", "）", "：", "；", "［", "］", "＜", "＞", "＝", "＠", "＃", "＄", "％", "＆", "＊", "＋", "－", "／", "＼", "＾", "｜", "～", "＿", "＇", "＂", "｀", "｛", "｝", "＜", "＞", "＝", "＼", "｜", "＠", "＃", "＄", "％", "＾", "＆", "＊", "（", "）", "＿", "＋", "｀", "～", "｛", "｝", "［", "］", "：", "；", "＂", "＇", "｜", "＼", "＜", "＞", "？", "！", "。", "、", "・", "…", "ー", "゛", "゜", "ゝ", "ゞ"]


def get_initial_message_list(proeficiency: int):
    difficulty = ["JLPT N3", "JLPT N1", "Japanese Native"]
    user_difficulty_setting = difficulty[proeficiency-1%len(difficulty)]

    return [
            {
            "role": "system",
            "content": f"I am a Japanese conversation bot designed to speak on a level similar to {user_difficulty_setting}.\n\nI will have basic conversation with the user.\nI will add a table at the end of the message containing the hiragana for every word used in my answer to the user, as well as the word itself, and the meaning of the word in the context of the conversation. This table will include ALL the words I use (no limits, the more words, the better), no matter how simple or complicated the words are. The table should be as long as possible, and contain EVERY SINGLE WORD I say in my main message"
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


def get_current_rtk_level(level):
    with open('config/kanji_list.json') as file:
        rtk_kanji_list = json.load(file)

    MAX_RTK_KANJI_NUMBER = level
    if MAX_RTK_KANJI_NUMBER > len(rtk_kanji_list):
        MAX_RTK_KANJI_NUMBER = len(rtk_kanji_list)
    rtk_kanji_list = rtk_kanji_list[:MAX_RTK_KANJI_NUMBER]
    return {obj["kanji"]: obj["rtk_order"] for obj in rtk_kanji_list}

def toggle_word_kanji_to_hiragana(word, username):
    db = UserConfigDB()
    user = db.get_user(username)
    known_words = user["known_kanjis"]

    if word in known_words:
        known_words.remove(word)
        status = False
    else:
        known_words.append(word)
        status = True

    db.update_field(username, 'known_kanjis', known_words)

    return status

def get_known_words(username):
    db = UserConfigDB()
    user = db.get_user(username)
    return user["known_kanjis"]
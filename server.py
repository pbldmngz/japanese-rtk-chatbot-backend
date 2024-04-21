from flask import Flask, request, jsonify
from chatbot import send_user_message, set_current_rtk_level, set_chat_japanese_proficiency, set_gpt_model, toggle_word_kanji_to_hiragana

app = Flask(__name__)

@app.route('/chat/<int:difficulty_level>/<int:rtk_level>/<string:session_id>/', methods=['POST'])
def process_text(difficulty_level, rtk_level, session_id):
    data = request.get_json()
    japanese_text = data.get('user_input', '')

    difficulty = ["JLPT N3", "JLPT N1", "Japanese Native"]
    user_difficulty_setting = difficulty[difficulty_level-1%len(difficulty)]

    set_chat_japanese_proficiency(user_difficulty_setting)
    set_current_rtk_level(rtk_level)
    # set_gpt_model("gpt-3.5-turbo-0125")
    set_gpt_model("gpt-4-turbo")

    response = send_user_message(japanese_text)

    return jsonify(response)

@app.route('/word/<int:word>/', methods=['POST'])
def toggle_kanji(word):
    is_kanji = toggle_word_kanji_to_hiragana(word)
    return jsonify({"message": f"Word {word} will be shown as {'kanji' if is_kanji else 'hiragana'}"})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)

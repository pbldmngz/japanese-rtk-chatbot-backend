from __init__ import app
from flask import request, jsonify
from utils.chatbot import send_user_message
from utils.settings import toggle_word_kanji_to_hiragana, get_initial_message_list
from utils.database import UserConfigDB
import sqlite3

@app.after_request
def middleware_for_response(response):
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add(
        "Access-Control-Allow-Origin",
        "https://rtk-chatbot.vercel.app",
    )
    response.headers.add("Access-Control-Allow-Methods", "GET,HEAD,OPTIONS,POST,PUT,DELETE")
    response.headers.add(
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Headers, Access-Control-Allow-Origin, Authorization, withcredentials, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers",
    )

    return response

@app.route('/chat/<string:username>', methods=['POST'])
def process_text(username):
    data = request.get_json()
    japanese_text = data.get('user_input', '')

    response = send_user_message(japanese_text, username)

    return jsonify(response)

@app.route('/word/<string:username>/<string:word>', methods=['GET'])
def toggle_kanji(username, word):
    is_kanji = toggle_word_kanji_to_hiragana(word, username)
    return jsonify({"message": f"Word {word} will be shown as {'kanji' if is_kanji else 'hiragana'}"})

@app.route('/user', methods=['POST'])
def add_user():
    db = UserConfigDB()
    user = request.get_json()
    required_keys = ['username', 'difficulty_level', 'rtk_level', 'word_spacing', 'input_mode', 'known_kanjis', 'message_log']
    if not all(key in user for key in required_keys):
        user['difficulty_level'] = user.get('difficulty_level', 0)
        user['rtk_level'] = user.get('rtk_level', 0)
        user['word_spacing'] = user.get('word_spacing', 0)
        user['input_mode'] = user.get('input_mode', False)
        user['known_kanjis'] = user.get('known_kanjis', [])
        user['message_log'] = user.get('message_log', get_initial_message_list(user.get('difficulty_level', 0)))
        user['gpt_model'] = user.get('gpt_model', 'gpt-4-turbo')
    try:
        db.add_user(user)
        return jsonify(db.get_user(user['username']))
    except sqlite3.IntegrityError:
        return jsonify({"message": "User already exists"}), 400

@app.route('/user/<string:username>', methods=['GET'])
def get_user(username):
    db = UserConfigDB()
    user = db.get_user(username)
    if user is None:
        return jsonify({"message": "User not found"}), 404
    return jsonify(user)

@app.route('/user/<string:username>', methods=['PUT'])
def update_user(username):
    db = UserConfigDB()
    user = db.get_user(username)
    if user is None:
        return jsonify({"message": "User not found"}), 404

    properties = request.get_json()
    # other properties are for system use only
    valid_keys = ['difficulty_level', 'rtk_level', 'word_spacing', 'input_mode']

    for key, value in properties.items():
        if key not in valid_keys:
            return jsonify({"message": f"Invalid key: {key}"}), 400
        db.update_field(username, key, value)

    return jsonify({"message": "User updated successfully"})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
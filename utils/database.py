from __init__ import app
from flask import g
import sqlite3
import json

class UserConfigDB:
    def __init__(self):
        self.DATABASE = 'config/user_config.db'
        self.conn = self.get_db()
        self.cursor = self.conn.cursor()
        self.create_table()

    def get_db(self):
        if 'db' not in g:
            g.db = sqlite3.connect(self.DATABASE)
        return g.db

    @app.teardown_appcontext
    def close_db(error):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS UserConfig (
                username TEXT PRIMARY KEY,
                difficulty_level INTEGER,
                rtk_level INTEGER,
                word_spacing INTEGER,
                input_mode BOOLEAN,
                known_kanjis TEXT,
                message_log TEXT,
                gpt_model TEXT
            )
        ''')
        self.conn.commit()

    def get_all_users(self):
        self.cursor.execute('SELECT * FROM UserConfig')
        rows = self.cursor.fetchall()
        users = []
        for row in rows:
            user = {
                'username': row[0],
                'difficulty_level': row[1],
                'rtk_level': row[2],
                'word_spacing': row[3],
                'input_mode': bool(row[4]),
                'known_kanjis': json.loads(row[5]),
                'message_log': json.loads(row[6]),
                'gpt_model': row[7]
            }
            users.append(user)
        return users

    def get_user(self, username):
        self.cursor.execute('SELECT * FROM UserConfig WHERE username = ?', (username,))
        row = self.cursor.fetchone()
        if row is None:
            return None
        user = {
            'username': row[0],
            'difficulty_level': row[1],
            'rtk_level': row[2],
            'word_spacing': row[3],
            'input_mode': bool(row[4]),
            'known_kanjis': json.loads(row[5]),
            'message_log': json.loads(row[6]),
            'gpt_model': row[7]
        }
        return user

    def update_field(self, username, field, value):
        if field in ['known_kanjis', 'message_log']:
            value = json.dumps(value)
        self.cursor.execute(f'UPDATE UserConfig SET {field} = ? WHERE username = ?', (value, username))
        self.conn.commit()

    def add_user(self, user):
        known_kanjis = json.dumps(user['known_kanjis'])
        message_log = json.dumps(user['message_log'])
        self.cursor.execute('''
            INSERT INTO UserConfig (
                username,
                difficulty_level,
                rtk_level,
                word_spacing,
                input_mode,
                known_kanjis,
                message_log,
                gpt_model
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user['username'],
            user['difficulty_level'],
            user['rtk_level'],
            user['word_spacing'],
            user['input_mode'],
            known_kanjis,
            message_log,
            user['gpt_model']
        ))
        self.conn.commit()
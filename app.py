from flask import Flask, request, jsonify, session, render_template
import sqlite3
from flask_cors import CORS
import hashlib

app = Flask(__name__)
app.secret_key = 'meowpower123'  # session 的安全用 key
CORS(app)  # 讓 JS 能跨域抓 API（必要時）

# 初始化 SQLite 資料庫（第一次會建表）
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()  # 程式一跑就建一次資料表（不會重複建）

# 註冊 API：收到 username+password，存進資料庫
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    hashpw = hashlib.sha256(password.encode('utf-8')).hexdigest()

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashpw))
        conn.commit()
        return jsonify({"success": True})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "帳號已存在"})
    finally:
        conn.close()

# 登入 API：查詢是否存在該帳號密碼
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    hashpw = hashlib.sha256(password.encode('utf-8')).hexdigest()

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashpw))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['username'] = username
        return jsonify({"success": True, "username": username}), render_template('/index.html')
    else:
        return jsonify({"success": False, "message": "帳號或密碼錯誤"})

# 登出 API：清掉 session
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({"success": True})

# 渲染 login 頁面
@app.route('/login')
def login_page():
    return render_template('login.html')

# 渲染 signup 頁面
@app.route('/signup')
def signup_page():
    return render_template('signup.html')

# 渲染首頁（或改成電子書頁面）
@app.route('/')
def home_page():
    return render_template('index.html')  # 或改成 memebook.html

#自介頁面更改（有點BUG)
@app.route('/profile')
def profile_page():
    return render_template('profile.html')

# 啟動後端
if __name__ == '__main__':
    app.run(debug=True, port=5050)
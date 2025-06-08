from flask import Flask, request, jsonify, session, render_template, redirect
import sqlite3
import hashlib
from flask_cors import CORS
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'meowpower123'
CORS(app)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # 使用者帳號表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            signup_time TEXT,
            last_login TEXT,
            last_logout TEXT
        )
    ''')

    # 行為紀錄表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # 迷因貼文表（預留）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT,
            description TEXT,
            image_path TEXT NOT NULL,
            upload_time TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id INTEGER PRIMARY KEY,
            display_name TEXT,
            avatar_url TEXT,
            bio TEXT,
            updated_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expired_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

def log_user_action(user_id, action):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()
    cursor.execute("INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
                   (user_id, action, timestamp))
    conn.commit()
    conn.close()

@app.route('/signup', methods=['POST'])#註冊邏輯
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    hashpw = hashlib.sha256(password.encode('utf-8')).hexdigest()

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, signup_time) VALUES (?, ?, ?)",
                       (username, hashpw, datetime.now().isoformat()))
        conn.commit()
        user_id = cursor.lastrowid
        session['username'] = username
        session['user_id'] = user_id
        log_user_action(user_id, 'signup')
        return jsonify({"success": True})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Username already exists"})
    finally:
        conn.close()

@app.route('/login', methods=['POST'])#登入邏輯
def login():
    data = request.get_json()
    username = data.get('username')#取得使用者名稱
    password = data.get('password')#取得使用者密碼
    hashpw = hashlib.sha256(password.encode('utf-8')).hexdigest()#使用SHA256加密使用者密碼

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, hashpw))#資料庫比對
    user = cursor.fetchone()

    if user:
        user_id = user[0]
        session['username'] = username
        session['user_id'] = user_id
        now = datetime.now().isoformat()
        cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (now, user_id))
        cursor.execute("INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, 'login', ?)",
                       (user_id, now))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "username": username})#登入成功
    else:
        conn.close()
        return jsonify({"success": False, "message": "Invalid username or password"})

@app.route('/logout', methods=['POST'])#登出邏輯
def logout():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "Not logged in"})

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("UPDATE users SET last_logout = ? WHERE id = ?", (now, user_id))
    cursor.execute("INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, 'logout', ?)",
                   (user_id, now))
    conn.commit()
    conn.close()

    session.clear()
    return jsonify({"success": True})

@app.route('/upload', methods=['POST'])
def upload_meme():
    if 'user_id' not in session:
        return redirect('/login')  # 未登入跳轉

    user_id = session['user_id']
    title = request.form.get('title')
    description = request.form.get('description')
    image = request.files.get('image')

    if not image:
        return "No image uploaded", 400

    filename = secure_filename(image.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(save_path)

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO memes (user_id, title, description, image_path, upload_time)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, title, description, save_path, datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return redirect('/')  # 成功後導回首頁



@app.route('/')
def home():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT memes.*, users.username FROM memes
        LEFT JOIN users ON memes.user_id = users.id
        ORDER BY upload_time DESC
    ''')
    memes = [
        {
            'title': row[2],
            'description': row[3],
            'image_path': row[4],
            'upload_time': row[5],
            'username': row[6]
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return render_template('index.html', username=session.get('username'),memes=memes)

@app.route('/login')
def login_page():
    return render_template('login.html', username=session.get('username'))

@app.route('/signup')
def signup_page():
    return render_template('signup.html', username=session.get('username'))

@app.route('/api/userinfo')
def userinfo():
    return jsonify({
        "username": session.get('username'),
        "user_id": session.get('user_id')
    })

@app.route('/memeupload')#迷因上傳路由
def memes():
    return render_template('memesupload.html', username=session.get('username'))

@app.route('/debug-session')
def debug_session():
    return jsonify(dict(session))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5050)
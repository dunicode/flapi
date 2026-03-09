###########################################################
# virtualenv -p python3 env                               #
# source env/bin/activate                                 #
# pip3 install flask flask-cors PyJWT gunicorn            #
# gunicorn --bind 0.0.0.0:8000 main:app                   #
###########################################################
import sqlite3
import jwt
import datetime
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__) 
CORS(app)

DATABASE = 'sqlite.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT NOT NULL, 
            email TEXT UNIQUE NOT NULL, 
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        db.commit()

init_db()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            # Expecting "Bearer <token>"
            token = token.split(" ")[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            cur = get_db().execute('SELECT * FROM users WHERE id = ?', (data['user_id'],))
            current_user = cur.fetchone()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data or 'name' not in data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Name, email and password are required"}), 400
    
    db = get_db()
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    try:
        cur = db.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', 
                         (data['name'], data['email'], hashed_password))
        db.commit()
        return jsonify({'id': cur.lastrowid, 'name': data['name'], 'email': data['email']}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password required"}), 400
    
    cur = get_db().execute('SELECT * FROM users WHERE email = ?', (data['email'],))
    user = cur.fetchone()
    
    if user and check_password_hash(user['password'], data['password']):
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({"message": "Login successful", "token": token})
        
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify(dict(current_user))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8000')

###########################################################
# virtualenv -p python3 env                               #
# source env/bin/activate                                 #
# pip3 install flask flask-cors                           #
# python3 main:app                                        #
###########################################################
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)   #DEFINE APP
CORS(app)               #ADD CORS 

# A simple in-memory data store for demonstration
users = {}
user_id_counter = 1

@app.route('/users', methods=['GET'])
def get_user():
    return jsonify(users)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_users(user_id):
    if user_id not in users:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(users[user_id])

@app.route('/users', methods=['POST'])
def create_user():
    global user_id_counter
    data = request.json
    if not data or 'name' not in data:
        return jsonify({"error": "Name is required"}), 400
    
    user_id = user_id_counter
    users[user_id] = {'id': user_id, 'name': data['name']}
    user_id_counter += 1
    return jsonify(users[user_id]), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    if user_id not in users:
        return jsonify({"error": "User not found"}), 404
    
    data = request.json
    if not data or 'name' not in data:
        return jsonify({"error": "Name is required"}), 400
    
    users[user_id]['name'] = data['name']
    return jsonify(users[user_id])

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if user_id not in users:
        return jsonify({"error": "User not found"}), 404
    
    del users[user_id]
    return jsonify({"message": "User deleted successfully"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8000')

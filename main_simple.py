###########################################################
# pip3 install flask flask-cors gunicorn                  #
# python3 main.py                                         #
# gunicorn --bind 0.0.0.0:5000 main:app                   #
###########################################################
import random
from flask import Flask
from flask import jsonify
from flask_cors import CORS

app = Flask(__name__)   #DEFINE APP
CORS(app)               #ADD CORS 

fruits = [
    {
        "id": 1,
        "name": "apple",
        "color": "red"
    },
    {
        "id": 2,
        "name": "orange",
        "color": "orange"
    },
    {
        "id": 3,
        "name": "banana",
        "color": "yellow"
    },
    {
        "id": 4,
        "name": "watermelon",
        "color": "green"
    },
    {
        "id": 5,
        "name": "coconut",
        "color": "brown"
    }
]

@app.route("/")
def index():
    response = fruits[random.randint(0, len(fruits) - 1)]
    return jsonify(response)

@app.route("/list")
def list():
    response = fruits
    return jsonify(response)

if __name__ == "__main__":
    app.run(host='0.0.0.0')

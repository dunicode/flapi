###########################################################
# pip3 install flask flask-cors flask-sqlalchemy gunicorn #
# python3 main.py                                         #
# gunicorn --bind 0.0.0.0:5000 main:app                   #
###########################################################
import os
from flask import Flask, request
from flask import jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)   #DEFINE APP
db = SQLAlchemy()       #ADD SQLALCHEMY
CORS(app)               #ADD CORS 

basedir = os.path.abspath(os.path.dirname(__file__))                                      #PROJECT DIR
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'sqlite.db') #USERNAME:PASSWORD@HOST:PORT/DATABASE
db.init_app(app)                                                                          #DB INIT

class Todo(db.Model):   #DATABASE MODEL
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    def json(self):     #DATA SERIALIZATION
        return {'id': self.id, 'title': self.title, 'description': self.description}

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except:
            return False
        
    def create(title, description):
        user = Todo(title=title, description=description)
        return user.save()
    
    def update(self):
        self.save()
        
    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except:
            return False

        
@app.route("/")                              #INDEX FUNCTION & ROUTE
def index():
    response = {'message': 'Hello World'}
    return jsonify(response)

@app.route("/todo", methods=['GET'])         #LIST FUNCTION & ROUTE
def todo_list():
    try:
        todos_json = [ todo.json() for todo in Todo.query.all() ] 
        response = {'todos': todos_json}
    except Exception as e:
        response = {'message': 'Error trying to get data: %s' % e}
    return jsonify(response)

@app.route("/todo", methods=['POST'])        #STORE FUNCTION & ROUTE
def todo_store():
    try:
        json = request.get_json(force=True)
        todo = Todo.create(json['title'], json['description'])
        response = {'todo': todo.json()}
    except Exception as e:
        response = {'message': 'Error trying to store data: %s' % e}
    return jsonify(response)

@app.route("/todo/<id>", methods=['GET'])    #VIEW FUNCTION & ROUTE
def todo_view(id):
    try:
        todo = Todo.query.filter_by(id=id).first()
        if todo is None:
            return jsonify({'message': 'Todo does not exists'}), 404
        response = {'todo': todo.json()}
    except Exception as e:
        response = {'message': 'Error trying to get data: %s' % e}
    return jsonify(response)

@app.route("/todo/<id>", methods=['PUT'])    #EDIT FUNCTION & ROUTE
def todo_edit(id):
    try:
        todo = Todo.query.filter_by(id=id).first()
        if todo is None:
            return jsonify({'message': 'Todo does not exists'}), 404
        
        json = request.get_json(force=True)
        if json.get('title') is None or json.get('description') is None:
            return jsonify({'message': 'Bad request'}), 400

        todo.title = json['title']
        todo.description = json['description']
        todo.update()
        response = {'todo': todo.json() }
    except Exception as e:
        response = {'message': 'Error trying to edit data: %s' % e}
    return jsonify(response)

@app.route("/todo/<id>", methods=['DELETE'])  #DELETE FUNCTION & ROUTE
def todo_delete(id):
    try:
        todo = Todo.query.filter_by(id=id).first()
        if todo is None:
            return jsonify({'message': 'Todo does not exists'}), 404
        todo.delete()
        response = {'todo': todo.json()}
    except Exception as e:
        response = {'message': 'Error trying to delete data: %s' % e}
    return jsonify(response)
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0')

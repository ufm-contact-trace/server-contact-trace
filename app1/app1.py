import os, redis
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo, MongoClient

ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
REDIS_CHANNEL = os.environ.get("REDIS_CHANNEL", 'mongo')


application = Flask(__name__)

"""
MongoDB setup
"""
# application.config["MONGO_URI"] = 'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_DATABASE']
# mongo = PyMongo(application)
# db = mongo.db
client = MongoClient(host=os.environ['MONGODB_HOSTNAME'],
                     port=27017,
                     username=os.environ['MONGODB_USERNAME'], 
                     password=os.environ['MONGODB_PASSWORD'],
                    authSource="admin")
db = client['flaskdb']
collection = db["data"]

"""
Redis setup
"""
channel = REDIS_CHANNEL
redis = redis.StrictRedis(host="redis", port=REDIS_PORT, db=0)


@application.route('/')
def index():
    return jsonify(
        status=True,
        message='Welcome to the Dockerized Flask MongoDB app!'
    )


@application.route('/sign-up', methods=['POST'])
def sign_up():
    data = request.get_json(force=True)
    hashed_email = data.get("hashed_email")
    email = data.get("email")
    redis.set(hashed_email, email)

    return jsonify(
        status=True,
        message='Sign up complete!'
    ), 200

@application.route('/contact', methods=['POST'])
def insert_contact():
    insertedIDs = None
    data = request.get_json(force=True)
    if isinstance(data, list):
        insertedIDs = collection.insert_many(data).inserted_ids
        contactID = ' '.join([str(elem) for elem in insertedIDs])
    else:
        insertedIDs = collection.insert_one(data).inserted_id
        contactID = insertedIDs
    
    redis.publish(channel, f"{contactID}")
    mongoMessage = f'The following contacts were saved succesfully: {contactID}'
    return jsonify(
        status=True,
        message=mongoMessage
    ), 201

@application.route('/todo')
def todo():
    _todos = db.todo.find()

    item = {}
    data = []
    for todo in _todos:
        item = {
            'id': str(todo['_id']),
            'todo': todo['todo']
        }
        data.append(item)

    return jsonify(
        status=True,
        data=data
    )

@application.route('/todo', methods=['POST'])
def createTodo():
    data = request.get_json(force=True)
    item = {
        'todo': data['todo']
    }
    db.todo.insert_one(item)

    return jsonify(
        status=True,
        message='To-do saved successfully!'
    ), 201



if __name__ == "__main__":
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)

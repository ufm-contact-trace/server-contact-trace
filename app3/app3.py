import os
import redis
import threading
import asyncio
import json
import requests
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo, MongoClient, ObjectId

ENVIRONMENT_DEBUG = os.environ.get("APP2_DEBUG", True)
ENVIRONMENT_PORT = os.environ.get("APP2_PORT", 8283)
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
REDIS_CHANNEL = os.environ.get("REDIS_CHANNEL", 'mongo')
REDIS_CHANNEL = os.environ.get("REDIS_CHANNEL", 'mongo')
REDIS_CHANNEL_NOTIFY = os.environ.get("REDIS_CHANNEL_NOTIFY", 'notify')


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
redis = redis.StrictRedis(host="redis", port=REDIS_PORT, db=0)
pubsub = redis.pubsub(ignore_subscribe_messages=True)
channel = REDIS_CHANNEL
channel_notify = REDIS_CHANNEL_NOTIFY

global_json = None



@application.route('/')
def index():
    return jsonify(
        status=True,
        message='Welcome to the Dockerized Flask MongoDB app!'
    )



def send_email(email):
    print(f"Sending email to: {email}")
    return requests.post(
        "https://api.mailgun.net/v3/sandboxc81fd26a81de4c27abb470681b17418d.mailgun.org/messages",
        auth=("api", "6340ce56e3ccef12c058cb910d94d158-2af183ba-36548ea8"),
        data={"from": "mailgun@sandboxc81fd26a81de4c27abb470681b17418d.mailgun.org",
              "to": [email],
              "subject": "Notificación de exposición a COVID-19",
              "text": "Ha sido expuesto a una persona con prueba de COVID-19 POSITIVA. \nFavor tomar las respectivas precauciones."})


# def message_handler(message):
#     """Converts message string to JSON.
#     Once invoked through asyncSUB() it handles
#     the message by converting it from string
#     to JSON and assigns it to 'global_json'
#     Note: global_json is probs deprecated   
#     """
#     json_message = None
#     message_data = message.get('data').decode('UTF-8')
#     send_email(message_data)
#     print(f"\n\nPUBLISHER APP 3: {message_data}\n\n")


# def asyncSUB():
    # """Subscribes to channel and sends message 
    # to handler.
    # When in need of reading messages this is the 
    # function to call. Once called it will subscribe 
    # asynchronously to channel (where channel = 'CHANNEL_NAME' 
    # defined on the first lines of this file).
    # p.run_in_thread(): Behind the scenes, this is
    # simply a wrapper around get_message() that runs 
    # in a separate thread, and use asyncio.run_coroutine_threadsafe() 
    # to run coroutines.
    # Coroutine: Coroutines are generalization of subroutines. 
    # They are used for cooperative multitasking where a process 
    # voluntarily yields (give away) control periodically or when 
    # idle in order to enable multiple applications to be run 
    # simultaneously.
    # """
    # pubsub.subscribe(**{channel_notify: message_handler})
    # thread = pubsub.run_in_thread(sleep_time=30, daemon=True)
    # message = pubsub.get_message()
    # print(f"\n\nSUBSCRIBER MESSAGE: {message}")

# def process():
#     """Process messages from the pubsub stream."""
#     pubsub.subscribe(channel)
#     for raw_message in pubsub.listen():
#         if raw_message:
#             print(f"raw_message: {raw_message}")
#             continue
#         message = json.loads(raw_message["data"])
#         print(message)


if __name__ == "__main__":
    # asyncSUB()
    # process()
    pubsub.psubscribe(channel_notify)
    for new_message in pubsub.listen():
        print(f"for new_message: {new_message}")

    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT,
                    debug=ENVIRONMENT_DEBUG)

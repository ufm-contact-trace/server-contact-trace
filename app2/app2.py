import os
import redis
import threading
import asyncio
import json
import datetime
import requests
import time
import dateutil.parser
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo, MongoClient, ObjectId

ENVIRONMENT_DEBUG = os.environ.get("APP2_DEBUG", True)
ENVIRONMENT_PORT = os.environ.get("APP2_PORT", 8282)
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
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
        message='Welcome to the non Dockerized Flask MongoDB app!'
    )


def query_mongo(idListString):
    idList = idListString.split()
    user = ""
    date = ""
    contacts = []

    for eachId in idList:
        query_result = collection.find({"_id": ObjectId(eachId)})

        for doc in query_result:
            user = doc.get('user')
            date = doc.get('date')
            # for contact in doc['contacts']:
            # email = redis.get(contact['key']).decode('UTF-8')
            # print("\n")
            # print(f"key: {contact['key']}")
            # print(f"\temail: {email}")
            # print(f"\ttimestamp: {contact['timestamp']}")

    analyze(user, date)


def analyze(user, date):
    contacts = []
    today = datetime.datetime.now()
    d = datetime.timedelta(days=int(os.environ.get('DAYS')))
    a = today - d

    col = collection.find({'user': user}).sort(
        'date', -1).limit(int(os.environ.get('DAYS')))

    for eachCol in col:
        print(f"EachCol.day: {eachCol.get('day')}")
        # print(f"EachCol: {eachCol}")
        date = datetime.datetime.strptime(eachCol.get(
            'day'), '%Y-%m-%d')

        print(f"DATE: date: {date}")
        print(f"\ttype: {type(date)}")
        print(f"DATE: a: {a}")
        print(f"\ttype: {type(a)}")

        if date > a:
            print("IF")
            # print(f"EachCol: {eachCol}")
            for contact in eachCol.get('contacts'):
                user = redis.get(contact['key'])
                if user is not None:
                    user = user.decode('UTF-8')
                    contacts.append(user)
                else:
                    print("user is None")
        else:
            print("ELSE")

    contacts = list(set(contacts))

    print(f"Contacts: {contacts}")
    # redis.publish(channel_notify, f"{contacts}")

    for eachContact in contacts:
        redis.publish(channel_notify, f"{eachContact}")

      # 2014-12-13 22: 45: 01.743172
    # print("\nAnalize:")
    # print(f"\tDays to analize: {d}")
    # print(f"\tuser: {user}")
    # print(f"\ttimestamp: {date}")
    # if timestamp < 15 days, then publish info to notify
    # redis.publish(channel_notify, f"{user}")

        # send_email(eachContact)


def message_handler(message):
    """Converts message string to JSON.
    Once invoked through asyncSUB() it handles
    the message by converting it from string
    to JSON and assigns it to 'global_json'
    Note: global_json is probs deprecated   
    """
    json_message = None
    message_data = message.get('data').decode('UTF-8')
    query_mongo(message_data)
    print(f"\n\nPUBLISHER APP 2: {message_data}\n\n")


def asyncSUB():
    """Subscribes to channel and sends message 
    to handler.
    When in need of reading messages this is the 
    function to call. Once called it will subscribe 
    asynchronously to channel (where channel = 'CHANNEL_NAME' 
    defined on the first lines of this file).
    p.run_in_thread(): Behind the scenes, this is
    simply a wrapper around get_message() that runs 
    in a separate thread, and use asyncio.run_coroutine_threadsafe() 
    to run coroutines.
    Coroutine: Coroutines are generalization of subroutines. 
    They are used for cooperative multitasking where a process 
    voluntarily yields (give away) control periodically or when 
    idle in order to enable multiple applications to be run 
    simultaneously.
    """
    pubsub.subscribe(**{channel: message_handler})
    thread = pubsub.run_in_thread(sleep_time=0.1, daemon=True)
    message = pubsub.get_message()
    print(f"\n\nSUBSCRIBER MESSAGE: {message}")

# def process():
#     """Process messages from the pubsub stream."""
#     pubsub.subscribe(channel)
#     for raw_message in pubsub.listen():
#         if raw_message:
#             print(f"raw_message: {raw_message}")
#             continue
#         message = json.loads(raw_message["data"])
#         print(message)


# def send_email(email):
#     print(f"Sending email to: {email}")
#     return requests.post(
#         "https://api.mailgun.net/v3/sandboxc81fd26a81de4c27abb470681b17418d.mailgun.org/messages",
#         auth=("api", "APIKEY"),
#         data={"from": "mailgun@sandboxc81fd26a81de4c27abb470681b17418d.mailgun.org",
#               "to": [email],
#               "subject": "Notificación de exposición a COVID-19",
#               "text": "Ha sido expuesto a una persona con prueba de COVID-19 POSITIVA. \nFavor tomar las respectivas precauciones."})


if __name__ == "__main__":
    asyncSUB()
    # process()
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT,
                    debug=ENVIRONMENT_DEBUG)

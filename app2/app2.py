import os, redis,  threading, asyncio, json
from flask import Flask, request, jsonify

ENVIRONMENT_DEBUG = os.environ.get("APP2_DEBUG", True)
ENVIRONMENT_PORT = os.environ.get("APP2_PORT", 8080)
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
REDIS_CHANNEL = os.environ.get("REDIS_CHANNEL", 'mongo')

application = Flask(__name__)

redis = redis.StrictRedis(host="redis", port=REDIS_PORT, db=0)
pubsub = redis.pubsub(ignore_subscribe_messages=True)
channel =  REDIS_CHANNEL

global_json = None

@application.route('/')
def index():
    return jsonify(
        status=True,
        message='Welcome to the Dockerized Flask MongoDB app!'
    )


def message_handler(message):
    """Converts message string to JSON.
    Once invoked through asyncSUB() it handles
    the message by converting it from string
    to JSON and assigns it to 'global_json'
    Note: global_json is probs deprecated   
    """
    json_message = None
    message_data = message.get('data').decode('UTF-8')
    print(f"MY HANDLER: {message_data}")


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
    print(f"asyncSUB: message: {message}")

def process():
    """Process messages from the pubsub stream."""
    pubsub.subscribe(channel)
    for raw_message in pubsub.listen():
        if raw_message:
            print(f"raw_message: {raw_message}")
            continue
        message = json.loads(raw_message["data"])
        print(message)

if __name__ == "__main__":
    asyncSUB()
    # process()
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)

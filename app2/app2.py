import os
from flask import Flask, request, jsonify

application = Flask(__name__)



@application.route('/')
def index():
    return jsonify(
        status=True,
        message='Welcome to the Dockerized Flask MongoDB app!'
    )



if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP2_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP2_PORT", 8080)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)

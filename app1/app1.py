import os, redis
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo, MongoClient

# from app.py
from functools import wraps
import sys
import os
from flask import Flask, render_template, redirect, request, url_for, session
# coming from pyrebase4
import pyrebase
import requests
import json
from pyfcm import *

config = {
    "apiKey": "AIzaSyAkUg7mNxW-W1Oqe_Mn_F6wogH6wlz3lRc",
    "authDomain": "covid-relief-1d6c0.firebaseapp.com",
    "databaseURL": "https://covid-relief-1d6c0.firebaseio.com",
    "storageBucket": "covid-relief-1d6c0.appspot.com",
    "projectId": "covid-relief-1d6c0",
    "messagingSenderId": "965781285698",
    "appId": "1:965781285698:android:9ce59d336ebb319d3036db"

}

# init firebase
firebase = pyrebase.initialize_app(config)
# auth instance
auth = firebase.auth()
# real time database instance
dbfb = firebase.database();

# from app1.py

ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
REDIS_CHANNEL = os.environ.get("REDIS_CHANNEL", 'mongo')

application = Flask(__name__)
# secret key for the session
application.secret_key = os.urandom(24)

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


### A ESTE INDEX LE CAMBIÉ EL NOMBRE

@application.route('/1')
def index1():
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


@application.route('/sign-up-array', methods=['POST'])
def sign_up_array():
    data = request.get_json(force=True)
    for each in data:
        hashed_email = each.get("hashed_email")
        email = each.get("email")
        redis.set(hashed_email, email)

    return jsonify(
        status=True,
        message='Sign up complete!'
    ), 200


@application.route('/contact', methods=['POST'])
def insert_contact():
    data = request.get_json(force=True)
    list_collection = list(collection.find({'user': data.get('user'), 'day': data.get('day')}))

    if len(list_collection) == 0:
        status = 1
        insertedIDs = collection.insert_one(data).inserted_id
    else:
        status = 0
        users_contacts = dict(list_collection[0]).get('contacts')
        new_contacts = data.get('contacts')
        total_contacts = users_contacts + new_contacts
        collection.update_one(
            {
                'user': data.get('user'), 'day': data.get('day')
            },
            {
                '$set': {'contacts': total_contacts}
            })
        list_collection = list(collection.find({'user': data.get('user'), 'day': data.get('day')}))

        
    mongoMessage = f"The following contacts were saved succesfully: Status: {status} \n {list_collection}"

    return jsonify(
        status=True,
        message=mongoMessage
    ), 201

@application.route('/notify', methods=['POST'])
def notify_contact():
    insertedIDs = []
    data = request.get_json(force=True)
    col = collection.find({'user': data.get('user'), 'day': data.get('day')})
    list_collection = list(collection.find({'user': data.get('user'), 'day': data.get('day')}))

    if len(list_collection) == 0:
        status = 1
        insertedIDs = collection.insert_one(data).inserted_id
    else:
        status = 0
        users_contacts = dict(list_collection[0]).get('contacts')
        new_contacts = data.get('contacts')
        total_contacts = users_contacts + new_contacts
        collection.update_one(
            {
                'user': data.get('user'), 'day': data.get('day')
            },
            {
                '$set': {'contacts': total_contacts}
            })
        for itm in collection.find({'user': data.get('user'), 'day': data.get('day')}):
            insertedIDs = itm.get('_id')

    redis.publish(channel, f"{insertedIDs}")

    mongoMessage = f'The following contacts were saved succesfully: Status: {status} {insertedIDs}'

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

# from app.py
# decorator to protect routes
def isAuthenticated(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # check for the variable that pyrebase creates
        if not auth.current_user != None:
            return redirect(url_for('signup'))
        return f(*args, **kwargs)

    return decorated_function


# index route
@application.route("/")
def index():
    return render_template("index.html")


@application.route("/about-us")
def about():
    return render_template("about-us.html")


@application.route("/test")
def test():
    business = dbfb.child("business").get().val().values()
    medicina = dbfb.child("medicina").get().val().values()
    psicologia = dbfb.child("psicología").get().val().values()
    tecnologia = dbfb.child("tecnología").get().val().values()
    approveBusiness = dbfb.child("business").get()
    # print(allposts.val(), file=sys.stderr)
    return render_template("test.html", business=business, medicina=medicina, psicologia=psicologia,
                           tecnologia=tecnologia,
                           approveBusiness=approveBusiness)


@application.route("/aprobar")
def aprobar():
    business = []
    business_keys = []
    business_response = dbfb.child("business").get()
    counter = 0
    for keys in business_response.val():
        print(type(keys))
        business_keys.append(keys)
    for dict_business in business_response.val().values():
        dict_business["ID"] = business_keys[counter]
        business.append(dict_business)
        counter += 1

    medicina = []
    medicina_keys = []
    medicina_response = dbfb.child("medicina").get()
    counter = 0
    for keys in medicina_response.val():
        print(type(keys))
        medicina_keys.append(keys)
    for dict_medicina in medicina_response.val().values():
        print("dict", type(dict_medicina))
        print(dict_medicina)
        dict_medicina["ID"] = medicina_keys[counter]
        medicina.append(dict_medicina)
        counter += 1

    psicologia = []
    psicologia_keys = []
    psicologia_response = dbfb.child("psicología").get()
    counter = 0
    for keys in psicologia_response.val():
        print(type(keys))
        psicologia_keys.append(keys)
    for dict_psicologia in psicologia_response.val().values():
        dict_psicologia["ID"] = psicologia_keys[counter]
        psicologia.append(dict_psicologia)
        counter += 1

    tecnologia = []
    tecnologia_keys = []
    tecnologia_response = dbfb.child("tecnología").get()
    counter = 0
    for keys in tecnologia_response.val():
        print(type(keys))
        tecnologia_keys.append(keys)
    for dict_tecnologia in tecnologia_response.val().values():
        dict_tecnologia["ID"] = tecnologia_keys[counter]
        tecnologia.append(dict_tecnologia)
        counter += 1

    # print(allposts.val(), file=sys.stderr)
    return render_template("aprobar.html", business=business, medicina=medicina, psicologia=psicologia,
                           tecnologia=tecnologia)


@application.route("/notification")
def notification():
    push_service = FCMNotification(
        api_key="AAAA4N0M60I:APA91bHGmWiGRCEO4mZABGz1cKyjt9lt-T_wd8CY2tF5DhXr0SNcpFdgrMMa67tM04NwI6koQWAdL7X6mPY4U5ZEs0rnW5qnmJ36oMjJHpXx6gz7OHJpobPZeOeFJxvNYAl7LceY-kEL")
    message_title = "Nueva publicación"
    message_body = "Te invitamos a revisar la aplicación"
    result = push_service.notify_topic_subscribers(topic_name="publicaciones",
                                                   message_body=message_body,
                                                   message_title=message_title)
    return result


@application.route("/estadisticas")
def estadisticas():
    return render_template("estadisticas.html")


# signup route
@application.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # get the request form data
        email = request.form["email"]
        password = request.form["password"]
        try:
            # create the user
            auth.create_user_with_email_and_password(email, password);
            # login the user right away
            user = auth.sign_in_with_email_and_password(email, password)
            # session
            user_id = user['idToken']
            user_email = email
            session['usr'] = user_id
            session["email"] = user_email
            return redirect("/")
        except:
            return render_template("login.html", message="Correo en uso, prueba con otro")

    return render_template("signup.html")


# login route
@application.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # get the request data
        email = request.form["email"]
        password = request.form["password"]
        try:
            # login the user
            user = auth.sign_in_with_email_and_password(email, password)
            # set the session
            user_id = user['idToken']
            user_email = email
            session['usr'] = user_id
            session["email"] = user_email
            return redirect("/")

        except:
            return render_template("login.html", message="Credenciales incorrectas")

    return render_template("login.html")


# logout route
@application.route("/logout")
def logout():
    # remove the token setting the user to None
    auth.current_user = None
    # also remove the session
    # session['usr'] = ""
    # session["email"] = ""
    session.clear()
    return redirect("/")


@application.route("/data")
def data():
    url = "https://covid-relief-1d6c0.firebaseio.com/.json"
    params = dict(

    )
    # resp = requests.get(url=url, params=params)
    resp = requests.get(url=url)
    if (resp.status_code == 200):
        data = resp.json()
        return data
    else:
        print(str(resp.status_code) + " " + str(resp))
        print(result)
    return ""


@application.route("/approve")
def approve():
    idPost = request.args.get('post')
    category = request.args.get('category')
    url = "https://covid-relief-1d6c0.firebaseio.com/"
    params = dict(

    )
    print(url + category + "/" + idPost + ".json")
    # resp = requests.get(url=url, params=params)
    resp = requests.get(url=url + category + "/" + idPost + ".json")
    if (resp.status_code == 200):
        data = resp.json()
        data['Estado'] = "approved"
        resp_put = requests.put(url=url + category + "/" + idPost + ".json", data=json.dumps(data))
        return {'response': str(resp_put.status_code), 'data': data, 'type': str(type(data))}
    else:
        print(str(resp.status_code) + " " + str(resp))
        print(result)
    return {'response': 400}


@application.route("/deny")
def deny():
    idPost = request.args.get('post')
    category = request.args.get('category')
    url = "https://covid-relief-1d6c0.firebaseio.com/"
    params = dict(

    )
    print(url + category + "/" + idPost + ".json")
    # resp = requests.get(url=url, params=params)
    resp = requests.get(url=url + category + "/" + idPost + ".json")
    if (resp.status_code == 200):
        data = resp.json()
        data['Estado'] = "denied"
        resp_put = requests.put(url=url + category + "/" + idPost + ".json", data=json.dumps(data))
        return {'response': str(resp_put.status_code), 'data': data, 'type': str(type(data))}
    else:
        print(str(resp.status_code) + " " + str(resp))
        print(result)
    return ""


if __name__ == "__main__":
    application.run(host='0.0.0.0', port=80, debug=True)

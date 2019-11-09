import pymongo,datetime,hashlib
from flask import Flask, render_template, url_for, redirect, request ,flash ,session
from pymongo import MongoClient
from flask_mail import Mail,Message
import os

app = Flask(__name__)

file = open("db_name","r")
username = file.read()
file = open("db_pass","r")
password = file.read()
client = pymongo.MongoClient("mongodb+srv://"+username+":"+password+"@cluster0-2ogac.mongodb.net/test?retryWrites=true&w=majority")
db = client["ride-a-bike"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup',methods = ['POST','GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    else:
        return "welcome"

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method=="GET":
        return render_template("login.html")
    else:
        return "welcome"

@app.errorhandler(404)
def notFound(e):
    return render_template("404.html"), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000, threaded = True, debug = True)
import pymongo,datetime,hashlib
from flask import Flask, render_template, url_for, redirect, request ,flash ,session
from pymongo import MongoClient
from flask_mail import Mail,Message
import os

app = Flask(__name__)

app.secret_key = 'Ride-a-Bike'

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
        if request.form['name']=="" or request.form['email']=="" or request.form['phone_number']=="" or request.form['gender']=="" or request.form['blood_group']=="" or request.form['dob']=="" or request.form['dl_number']=="" or request.form['dl_valid_till']=="" or request.form['password']=="" :
            return redirect('/signup')
        password = request.form['password']
        pass_256 = hashlib.sha256(password.encode())
        pass_encrypt = pass_256.hexdigest()
        cred = {"name":request.form['name'],"email":request.form['email'],"phone_number":request.form['phone_number'],"gender":request.form['gender'],"blood_group":request.form['blood_group'],"dob":request.form['dob'],"dl_number":request.form['dl_number'],"dl_valid_till":request.form['dl_valid_till'],"password":pass_encrypt}
        db.details.insert(cred) 
        session['username'] = request.form['name']
        return "welcome"

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method=="GET":
        return render_template("login.html")
    else:
        try:
            if request.form['name'] == "admin" and request.form['password'] == "admin":
                session['username'] = request.form['name']
                return "admin"
            elif request.form['name'] == "manager" and request.form['password'] == "maanger":
                session['username'] = request.form['name']
                return "manager"
            else:
                password = request.form['password']
                pass_256 = hashlib.sha256(password.encode())
                pass_encrypt = pass_256.hexdigest()
                x = db.details.find({"name":request.form['name']})
                if x[0]["password"] == pass_encrypt :
                    session['username'] = request.form['name']
                    return redirect('/view')
                else:
                    return redirect('/login')
        except:
            return redirect('/login')

@app.route('/view')
def view():
    if 'username' in session:
        return render_template("view.html")
    else:
        return "You are not logged in <br><a href = '/login'></b>" + "click here to log in</b></a>"

@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect('/')


@app.errorhandler(404)
def notFound(e):
    return render_template("404.html"), 404

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000, threaded = True, debug = True)
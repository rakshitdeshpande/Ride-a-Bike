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
        return redirect('/home')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method=="GET":
        return render_template("login.html")
    else:
        try:
            if request.form['name'] == "admin" and request.form['password'] == "admin":
                session['username'] = request.form['name']
                return "admin"
            elif request.form['name'] == "manager" and request.form['password'] == "manager":
                session['username'] = request.form['name']
                return redirect('/manager')
            else:
                password = request.form['password']
                pass_256 = hashlib.sha256(password.encode())
                pass_encrypt = pass_256.hexdigest()
                x = db.details.find({"name":request.form['name']})
                if x[0]["password"] == pass_encrypt :
                    session['username'] = request.form['name']
                    return redirect('/home')
                else:
                    return redirect('/login')
        except:
            return redirect('/login') 

@app.route('/home')
def home():
    if 'username' in session and session['username'] != "manager":
        username = session['username']
        scooter_details = db.scooter.find({})
        docking_station_details = db.docking_station.find({})
        return render_template("home.html",username = username,docking_station_details=docking_station_details)
    else:
        return "You are not logged in <br><a href = '/login'></b>" + "click here to log in</b></a>"

@app.route('/manager')
def manager():
    try:
        if 'username' in session and session['username'] == "manager":
            return render_template("manager.html")
        return "You are not logged in <br><a href = '/login'></b>" + "click here to log in</b></a>"
    except:
        return redirect('/manager')

@app.route('/add_scooter', methods = ['POST','GET'])
def add_scooter():
    # try:
        if 'username' in session and session['username'] == "manager":
            if request.method == 'GET' :
                docking_station_details = db.docking_station.find({})
                return render_template("add_scooter.html",docking_station_details = docking_station_details)
            else:
                data = {"registration_number":request.form['registration_number'],"insurance_number":request.form['insurance_number'],"insurance_valid_till":request.form['insurance_valid_till'],"docking_station":request.form['docking_station'],"ignition_status":"off","rider_name":"-"}
                db.scooter.insert(data)
                x = db.docking_station.find({"station_name":request.form['docking_station']})
                num = x[0]["no_of_scooters"]
                num = num + 1
                print(num)
                db.docking_station.update({"station_name":request.form['docking_station']},{"$set":{"no_of_scooters":num}})
                return redirect('/manager')
        else:
            return "You are not logged in <br><a href = '/login'></b>" + "click here to log in</b></a>"
    # except:
    #     return render_template("add_scooter.html")

@app.route('/start_ride', methods = ['POST','GET'])
def start_ride():
    try:
        if 'username' in session and session['username'] != "manager":
            if request.method == 'GET':
                username = session['username']
                scooter_data = db.scooter.find({})
                return render_template("start_ride.html",username = username,scooter_data = scooter_data)
            else:
                return redirect('/end_ride')
        else:
            return "You are not logged in <br><a href = '/login'></b>" + "click here to log in</b></a>"
    except:
        return render_template('/start_ride.html')

@app.route('/end_ride', methods = ['POST','GET'])
def end_ride():
    try:
        if 'username' in session and session['username'] != "manager":
            if request.method == 'GET':
                username = session['username']
                docking_station_data = db.docking_station.find({})
                return render_template("end_ride.html",username = username,docking_station_data = docking_station_data)
            else:
                return redirect('/bill')
        else:
            return "You are not logged in <br><a href = '/login'></b>" + "click here to log in</b></a>"
    except:
        return render_template('/end_ride.html')

@app.route('/bill')
def bill():
    try:
        if 'username' in session and session['username'] != "manager":
            a = datetime.datetime.now()
            time = a.strftime("%c")
            return render_template("bill.html",time = time)
        else:
            return "You are not logged in <br><a href = '/login'></b>" + "click here to log in</b></a>"
    except:
        return render_template("bill.html")

@app.route('/add_station',methods = ['POST','GET'])
def add_station():
    try :
        if request.method == 'POST':
            data = {"station_name":request.form["station_name"],"no_of_scooters":0}
            db.docking_station.insert(data)
            return "true"
        else:
            return render_template("manager.html")
    except:
        return render_template("manager.html")

@app.route('/remove_scooter',methods = ['POST','GET'])
def remove_scooter():
    try :
        if request.method == 'POST':
            return "request accepted!"
        else:
            return render_template("manager.html")
    except:
        return render_template("manager.html")
    
@app.route('/remove_station',methods = ['POST','GET'])
def remove_station():
    try :
        if request.method == 'POST':
            return "request accepted!"
        else:
            return render_template("manager.html")
    except:
        return render_template("manager.html")

@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect('/')


@app.errorhandler(404)
def notFound(e):
    return render_template("404.html"), 404

@app.route('/delete_scooter')
def delete_scooter():
    db.scooter.delete_many({})
    return render_template("index.html")

@app.route('/delete_station')
def delete_station():
    db.docking_station.delete_many({})
    return render_template("index.html")

@app.route('/delete_details')
def delete_details():
    db.docking_station.delete_many({})
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000, threaded = True, debug = True)
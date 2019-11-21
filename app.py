'''
        Ride-a-Bike
        Developer : Rakshit Deshpande
'''
import pymongo,datetime,hashlib,math,pytz
from flask import Flask, render_template, url_for, redirect, request ,flash ,session
from pymongo import MongoClient
from flask_mail import Mail,Message
import os

app = Flask(__name__)

app.secret_key = 'Ride-a-Bike'

#accesing environment variables
manager_name = os.environ['MANAGER_NAME']
manager_pass = os.environ['MANAGER_PASS']
db_username = os.environ['DB_USERNAME']
db_password = os.environ['DB_PASS']
id = os.environ['MAIL_PASS']
mail_id = os.environ['MAIL_ID']

client = pymongo.MongoClient("mongodb+srv://"+db_username+":"+db_password+"@cluster0-2ogac.mongodb.net/test?retryWrites=true&w=majority")
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
            # if request.form['name'] == "admin" and request.form['password'] == "admin":
            #     session['username'] = request.form['name']
            #     return "admin"
            if request.form['name'] == manager_name and request.form['password'] == manager_pass:
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

@app.route('/home',methods = ['POST','GET'])
def home():
    if 'username' in session and session['username'] != manager_name:
      if request.method == 'GET':
        username = session['username']
        scooter_details = db.scooter.find({})
        docking_station_details = db.docking_station.find({})
        return render_template("home.html",username = username,docking_station_details=docking_station_details)
      else:
          
          return redirect('/start_ride')
    else:
        return "You are not logged in <br><a href = '/login'></b>" + "click here to log in</b></a>"

@app.route('/manager')
def manager():
    try:
        if 'username' in session and session['username'] == manager_name:
            return render_template("manager.html")
        return "You are not logged in <br><a href = '/login'></b>" + "click here to log in</b></a>"
    except:
        return redirect('/manager')



@app.route('/add_scooter', methods = ['POST','GET'])
def add_scooter():
    try:
        if 'username' in session and session['username'] == manager_name:
            if request.method == 'GET' :
                docking_station_details = db.docking_station.find({})
                return render_template("add_scooter.html",docking_station_details = docking_station_details)
            else:
                data = {"registration_number":request.form['registration_number'],"insurance_number":request.form['insurance_number'],"insurance_valid_till":request.form['insurance_valid_till'],"docking_station":request.form["docking_station"],"ignition_status":"off","rider_name":"-"}
                x = db.scooter.find({"registration_number":request.form['registration_number']})
                y = db.scooter.find({"insurance_number":request.form['insurance_number']})
                docking_station_details = db.docking_station.find({})
                try :
                    if x[0] :
                        error = "A vehicle with registration number already exists!"
                    return render_template("add_scooter.html",error = error,docking_station_details = docking_station_details)
                except:
                    try:
                        if y[0] :
                            error = "Insurance Number is of different vehicle"
                            return render_template("add_scooter.html",error = error,docking_station_details = docking_station_details)
                    except:
                        db.scooter.insert(data)
                        x = db.docking_station.find({"station_name":request.form['docking_station']})
                        num = x[0]["no_of_scooters"]
                        num = num + 1
                        db.docking_station.update({"station_name":request.form['docking_station']},{"$set":{"no_of_scooters":num}})
                        return redirect('/manager')
        else:
            return "You are not logged in <br><a href = '/login'></b>" + "click here to log in</b></a>"
    except:
        return render_template("add_scooter.html")

@app.route('/start_ride', methods = ['POST','GET'])
def start_ride():
    try:
        if 'username' in session and session['username'] != manager_name:
            if request.method == 'POST':
                username = session['username']
                scooter_data = db.scooter.find({"docking_station":request.form['station_name']})
                db.details.update({"name":session['username']},{"$set":{"from":request.form['station_name']}})
                return render_template("start_ride.html",username = username,scooter_data = scooter_data)
            else: 
                return render_template("start_ride.html")
        else:
            return "You are not logged in <br><a href = '/login'></b>" + "click here to log in</b></a>"
    except:
        return redirect('/start_ride')

@app.route('/end_ride', methods = ['POST','GET'])
def end_ride():
    try:
        if 'username' in session and session['username'] != manager_name:
            if request.method == 'POST':
                username = session['username']
                docking_station_data = db.docking_station.find({})
                a = datetime.datetime.now(pytz.timezone('Asia/Calcutta'))
                start_time = a.strftime("%c")
                data = db.scooter.find({"registration_number":request.form['registration_number']})
                station  = data[0]["docking_station"]
                db.details.update({"name":session['username']},{"$set":{"registration_number":request.form['registration_number'],"start_time":start_time}})
                db.scooter.update({"registration_number":request.form['registration_number']},{"$set":{"rider_name":session['username'],"ignition_status":"on","docking_station":"-"}})
                details = db.docking_station.find({"station_name":station})
                num = details[0]["no_of_scooters"]
                num = num - 1
                db.docking_station.update({"station_name":station},{"$set":{"no_of_scooters":num}})
                return render_template("end_ride.html",username = username,docking_station_data = docking_station_data)
            else:
                return redirect('/end_ride')
        else:
            return "You are not logged in <br><a href = '/login'></b>" + "click here to log in</b></a>"
    except:
        return render_template("start_ride.html")

    
@app.route('/bill',methods = ['POST','GET'])
def bill():
    try:
        if 'username' in session and session['username'] != manager_name:
          if request.method == 'POST':
            a = datetime.datetime.now(pytz.timezone('Asia/Calcutta'))
            end_time = a.strftime("%c")
            db.details.update({"name":session['username']},{"$set":{"destination":request.form['destination'],"end_time":end_time}})
            db.scooter.update({"rider_name":session['username']},{"$set":{"docking_station":request.form['destination'],"ignition_status":"off","rider_name":"-"}})
            details = db.docking_station.find({"station_name":request.form['destination']})
            print(details[0]["no_of_scooters"])
            num = details[0]["no_of_scooters"]
            num = num + 1
            db.docking_station.update({"station_name":request.form['destination']},{"$set":{"no_of_scooters":num}})
            data = db.details.find({"name":session['username']})
            start_time = data[0]["start_time"]
            a = start_time.split(" ")
            time = a[3].split(":")
            before_hour = int(time[0])
            before_min = int(time[1])
            
            a = end_time.split(" ")
            time = a[3].split(":")
            after_hour = int(time[0])
            after_min = int(time[1])
            #calculaitng ride timming
            hour = after_hour - before_hour -1
            minutes = after_min + (60 - before_min) + (hour*60)
            quo = int(minutes/30)
            rem = minutes%30
            if rem == 0:
                amount = quo*50
            else:
                amount = (quo + 1 )*50
            details = {"name":session['username'],"registration_number":data[0]["registration_number"],"from":data[0]["from"],"start_time":data[0]["start_time"],"destination":data[0]["destination"],"end_time":data[0]["end_time"],"amount":amount,"duration":minutes}
            db.logs.insert(details)
            db.details.update({"name":session['username']},{"$set":{"from":"-","desination":"-","registration_number":"-","start_time":"-","end_time":"-"}})
            return render_template("bill.html",time = end_time,data = data,minutes = minutes,amount = amount,username = session['username'])
          else:
              return render_template("bill.html")
        else:
            return "You are not logged in <br><a href = '/login'></b>" + "click here to log in</b></a>"
    except:
        return redirect('/end_ride')

@app.route('/add_station',methods = ['POST','GET'])
def add_station():
    try :
      if 'username' in session and session['username'] == manager_name:
        if request.method == 'POST':
            data = {"station_name":request.form["station_name"],"no_of_scooters":0}
            db.docking_station.insert(data)
            return render_template("manager.html")
        else:
            return render_template("manager.html")
      else:
          "You are not logged in <br><a href = '/login'></b>" + "click here to log in</b></a>"
    except:
        return render_template("manager.html")

@app.route('/remove_scooter',methods = ['POST','GET'])
def remove_scooter():
    try :
        if 'username' in session and session['username'] == manager_name:
            if request.method == 'POST':
                return "request accepted!"
            else:
                return render_template("manager.html")
    except:
        return render_template("manager.html")
    
@app.route('/remove_station',methods = ['POST','GET'])
def remove_station():
    try :
        if 'username' in session and session['username'] == manager_name:
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
  try:
    if 'username' in session and session['username'] == manager_name:
        db.scooter.delete_many({})
        return render_template("index.html")
    else:
        "You are not logged in <br><a href = '/login'></b>" + "click here to log in</b></a>"
  except:
      return redirect("/")

@app.route('/delete_station')
def delete_station():
  try:
    if 'username' in session and session['username'] == manager_name:
        db.docking_station.delete_many({})
        return render_template("index.html")
    else:
        "You are not logged in <br><a href = '/login'></b>" + "click here to log in</b></a>"
  except:
      return redirect("/")

@app.route('/delete_details')
def delete_details():
  try:
    if 'username' in session and session['username'] == manager_name:
        db.details.delete_many({})
        return render_template("index.html")
    else:
        "You are not logged in <br><a href = '/login'></b>" + "click here to log in</b></a>"
  except:
      return redirect("/")

@app.route('/clear_logs')
def clear_logs():
  try:
    if 'username' in session and session['username'] == manager_name:
        db.logs.delete_many({})
        return render_template("index.html")
    else:
        "You are not logged in <br><a href = '/login'></b>" + "click here to log in</b></a>"
  except:
      return redirect("/")

    
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000, threaded = True, debug = True)
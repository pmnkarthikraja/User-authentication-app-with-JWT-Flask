
from base64 import encode
import email
from gzip import FNAME
from imp import reload
from multiprocessing import connection
import smtplib
import random
from sqlite3 import Cursor, connect
import json
from flask_bcrypt import Bcrypt
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask,request,render_template,url_for,jsonify,session,redirect
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from flask_socketio import SocketIO, emit
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager


mydb=mysql.connector.connect(host='localhost',user='root', password='root!@#123', database='userlogin',auth_plugin='mysql_native_password')
mycursor=mydb.cursor()
aa=1

app=Flask(__name__)

##fernet
key1 = Fernet.generate_key()
fernet = Fernet(key1)


app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "asdfghjklqwertyuiopzxcvbnm"  # Change this!
jwt = JWTManager(app)

@app.route("/", methods=['POST','GET'])
def home(a=True,entered_password=True):
    global aa
    if aa==1:
        session['token']=None
        aa=2
    if session["token"]!=None:
        return render_template("index.html")
    if a!=False and entered_password!=False:
        return render_template("home.html",showlogic="False")
    if a!=False and entered_password==False:
        return render_template("home.html",showlogic="False",entered_password="False")
    else:
        print(a)
        return render_template("home.html",showlogic="True")

@app.route("/signup",methods=['POST','GET'])
def signup():
    return render_template("signup.html")


@app.route("/success-login",methods=['GET','POST'])
def successlogin():
    email=request.form.get("email")
    password=request.form.get("password")
    #print(password)
    # password_encrypt=generate_password_hash(password)
    #jwt token generation
    access_token=create_access_token(identity=email)
    a=access_token
    session["token"]=a
    session["email"]=email
    query="SELECT email,password FROM accountdetails"
    mycursor.execute(query)
    rows=mycursor.fetchall()
    exist=None
    if len(rows)==0:
        return render_template("home.html",showlogic="True")  
    else:
        for row in rows:
            if row[0]==email:
                # print("row1:",row[1])
                # print("password:",password)
                
                if check_password_hash(row[1],password):
                    exist=True
                    return render_template("index.html")
                else:
                    return render_template("home.html",showlogic="False",entered_password="False")
            else:
                exist=False
    if exist is False:
        return render_template("home.html",showlogic="True")

        
@app.route("/home",methods=['POST','GET'])
def successsignup():
    fname=request.form.get("firstname")
    lname=request.form.get("lastname")
    dob=request.form.get("dob")
    email=request.form.get("email")
    password=request.form.get("password")
    enc_password=generate_password_hash(password)
    query="insert into accountdetails (firstname,lastname,dob,email,password) values ('%s','%s','%s','%s','%s');"%(fname,lname,dob,email,enc_password)
    mycursor.execute(query)
    mydb.commit()

    return render_template("home.html",accountcreated=True)



@app.route("/signout",methods=['POST','GET'])
def signout():
    session["token"]=None
    session["email"]=None
    return redirect(url_for('home'))

@app.route("/forget-password",methods=['POST','GET'])
def forgetpassword():
    return render_template("forgetpass.html",a=False)

@app.route("/otp-verifying",methods=['POST','GET'])
def otpverify():
    # global otp
    # global reset_email
    reset_email=request.form.get("mail")
    print("reset_email---:",reset_email)
    query="select email from accountdetails;"
    mycursor.execute(query)
    emails=mycursor.fetchall()
    next=False
    for Email in emails:
        if Email[0]==reset_email:
            next=True
    if next is True:
        connection=smtplib.SMTP("SMTP.gmail.com",587)
        connection.starttls()
        otp=random.randint(100000,999999)
        a=request.form.get("mail")
        if a is not None:
            connection.login(
            user="pmnkarthikrajanew@gmail.com",
            password="dqprwfqfzorlwcyd")
            connection.sendmail(
            from_addr="pmnkarthikrajanew@gmail.com",
            to_addrs=a,
            msg="Subject:PythonMail\n\nYour OTP for resetting password\n\n'%s'"%(otp))
            connection.close()
            return render_template("forgetpass.html",a=True,otp=otp,reset_email=reset_email,notregister=False)
    else:
        return render_template("forgetpass.html",notregister=True)


@app.route("/otp-verified",methods=['POST','GET'])
def otp_verified():
    user_otp=request.form.get("otp-entered")
    otp=request.form.get("main-otp")
    if user_otp != None:
        user_otp=int(user_otp)
    if user_otp==None:
        user_otp,otp=1,1
    reset_email=request.form.get("reset_email")
    print("reset email is: ",reset_email)
    print("otp is: ",otp)
    if user_otp==int(otp):
        return render_template("reset.html",reset_email=reset_email,success=None)
    else:
        return jsonify({"Status":"Fail","user_otp":user_otp,"otp":otp})

@app.route("/resetting",methods=['POST','GET'])
def reset():
    resetted_password=request.form.get("reset_password")
    reset_email=request.form.get("reset_email")
    print("reseted password: ",resetted_password)
    print("reset email is: ",reset_email)
    encrypt_password=generate_password_hash(resetted_password)
    if reset_email!=None:
        query="update accountdetails set password='%s' where email='%s';"%(encrypt_password,reset_email)
        mycursor.execute(query)
        mydb.commit()
        print("reset email stage completed")
    if reset_email=="None":
        print("session: ",session["email"])
        query="update accountdetails set password='%s' where email='%s';"%(encrypt_password,session["email"])
        mycursor.execute(query)
        mydb.commit()
        print("Finished")
        print("Final Finished")

    return render_template("reset.html",success=True)


# @app.route("/reset_inner",methods=['POST','GET'])
# def reset_inner():
#     return render_template("reset.html")


if __name__=="__main__":
    app.run(debug=True)

from datetime import datetime
from flask import render_template, Flask, escape, request, session, redirect, url_for
from flask_bootstrap import Bootstrap
import hashlib
import configparser

app = Flask(__name__)
Bootstrap(app)
app.secret_key=b'd#\t.gbn24#@-54_#\n/\\'

page_chat='chat.html'
page_login='login.html'
page_register='register.html'

messagesSoFar = []
limit=100
mesLengthLimit=200

configfile='users.properties'
userdata=configparser.RawConfigParser()
userdata.read(configfile)

@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        return redirect(url_for('message'))
    return render_template(page_login)

@app.route('/login', methods=['GET','POST'])
def login():
    message=None
    if 'username' in session:
        return sendChatPage()
    if request.method == 'POST':
        acquiredUname=request.form['usr']
        acquiredPsswd=request.form['pwd']
        if isUserValid(acquiredUname, acquiredPsswd):
            session['username']=acquiredUname
            return redirect(url_for('message'))
        message='Login unsuccessful. Please try again.'
    return render_template(page_login, mes=message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        usr=request.form['usr']
        pwd1=request.form['pwd1']
        pwd2=request.form['pwd2']
        if not pwd1 == pwd2:
            render_template(page_register,mes="Password doesn't match.")
        addUser(usr,pwd1)
        return redirect(url_for('login'))
    return render_template(page_register)

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/message', methods=['GET','POST'])
def message():
    if not 'username' in session:
        return render_template(page_login)

    user=session['username']

    if request.method ==  'POST':
        recmes=request.form['mes']
        if len(recmes) > mesLengthLimit:
            recmes = recmes[:mesLengthLimit]
        messagesSoFar.append('[' + getCurrentDatetime() + '] ['  + user + ']: ' + recmes)
    
    return sendChatPage()

def concatMessages():
    ret=""
    for i in messagesSoFar:
        ret = ret + "<br/>" + i
    return ret

def getCurrentDatetime():
    dateNow=datetime.now()
    return dateNow.strftime("%Y.%m.%d %H:%M:%S")

def addUser(uname, psswd):
    hashedPassword=hashlib.sha256(psswd.encode('utf-8')).hexdigest()
    userdata.set('users',uname,hashedPassword)
    with open(configfile,'w') as cfgfile:
        userdata.write(cfgfile)
    userdata.read(configfile)

def isUserValid(uname, psswd):
    if userdata.has_option('users',uname):
        storedPassword=userdata.get('users',uname)
        hashedPassword=hashlib.sha256(psswd.encode('utf-8')).hexdigest()
        if hashedPassword == storedPassword:
            return True
    return False

def sendChatPage():
    return render_template(page_chat, message=concatMessages(), usr=session['username'])


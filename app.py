from flask import Flask, render_template 
from flask import render_template
from flask import request
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from collections import defaultdict
from flask import Flask
from flask import Flask,flash,redirect,render_template,request,session,abort
import pymysql
from datetime import datetime as dt

app = Flask(__name__,static_folder='img')
app.secret_key = 'hogehoge'

def con():
    db = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='root',
        db='money',
        port= 13306,
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor,
    )
    return db    

def instartkinmu(kinmuti,Hourlywage):
    db=con()
    db.ping(reconnect=True)
    cur = db.cursor()
    sql = "INSERT INTO kinmu (kinmuti, Hourlywage) VALUES (%s, %s)"
    cur.execute(sql, (kinmuti,Hourlywage))
    db.commit()
    cur.close()
    db.close()
    
def instartkiroku(hiduke,iri,owari):
    db=con()
    db.ping(reconnect=True)
    cur = db.cursor()
    sql = "INSERT INTO kiroku (day,iri,owari) VALUES (%s, %s, %s)"
    cur.execute(sql, (hiduke,iri,owari))
    db.commit()
    cur.close()
    db.close()

def user():
    db=con()
    db.ping(reconnect=True)
    cur = db.cursor()
    sql = "select user, pass from users"
    cur.execute(sql)
    user = cur.fetchall()
    cur.close()
    db.close()
    return user

def userlogin(users,pass1):
    a=user()
    for i in range(len(a)):
        print(a[i])
        print(a[i]['user'])
        if  users == a[i]['user']:
            if pass1 == a[i]['user']:
                text = 'OK'
                session['logged_in'] = True
                return render_template('check.html', title='勤怠記録')
            else:
                text = 'passが違います.'
        else:
            text = 'idが違います'
    return text

def simplecheck(kadou,zikilyu):
    kin=float(kadou)*int(zikilyu)
    return kin

def kadou(iri,owari):
    iri = dt.strptime(iri, '%H:%M')
    owari = dt.strptime(owari, '%H:%M')
    kadou = owari-iri
    kadou = kadou.seconds
    kadou = kadou/3600
    print(kadou)

    return kadou

def keisan(kinmuti,kadou1):
    db=con()
    db.ping(reconnect=True)
    cur = db.cursor()
    sql = "select Hourlywage from kinmu WHERE kinmuti =%s"
    cur.execute(sql, (kinmuti))
    zikyu = cur.fetchall()
    cur.close()
    db.close()
    zikyu=zikyu[0]
    zikyu=zikyu['Hourlywage']
    return zikyu

def keisan1(kadou1,zilyu1):
    print(kadou1)
    if kadou1 >=9:
        kadou1 = kadou1 - 1.0
        print(kadou1)
    elif kadou1 >=6:
        kadou1 = kadou1 - 0.45
    kin=kadou1*zilyu1
    print(kin)
    return kin

def limit10():
    db=con()
    db.ping(reconnect=True)
    cur = db.cursor()
    sql = "select day,iri,owari from kiroku limit 30"
    cur.execute(sql)
    limit = cur.fetchall()
    cur.close()
    db.close()
    return limit

def instartk(hiduke,kilyuyo,kinmu):
    db=con()
    db.ping(reconnect=True)
    cur = db.cursor()
    sql = "INSERT INTO salary (day,kinmuti,salary) VALUES (%s, %s, %s)"
    cur.execute(sql, (hiduke,kinmu,kilyuyo))
    db.commit()
    cur.close()
    db.close()


@app.route('/')
def main():
    kin=0
    return render_template('index.html', title='給与チェッカー' ,kin=kin)
@app.route('/', methods=['POST'])

def post():
    kadou = request.form['name']
    zikilyu = request.form['name1']
    kin=simplecheck(kadou,zikilyu)
    return render_template('index.html', title='給与チェッカー',kin=kin)

@app.route('/kiroku')

def kiroku():
    if not session.get('logged_in'):
        return render_template('login.html',title='ログイン画面')
    else:
        limit=limit10()
        return render_template('check.html', title='勤怠記録',limit=limit)

@app.route('/kiroku', methods=['POST'])
def KirokuPost():
    hiduke = request.form['hiduke']
    iri    = request.form['iri']
    owari  = request.form['owari']
    kinmu  = request.form['kinmu']
    instartkiroku(hiduke,iri,owari)
    kadou1=kadou(iri,owari)
    zilyu1=keisan(kinmu,kadou1)
    kilyuyo=keisan1(kadou1,zilyu1)
    instartk(hiduke,kilyuyo,kinmu)
    return kiroku()

@app.route('/kinmu')
def kinmu():
    if not session.get('logged_in'):
        return render_template('login.html',title='ログイン画面')
    else:
        kin=0
        return render_template('kinmu.html', title='勤務場所登録' ,kin=kin)
    
@app.route('/kinmu', methods=['POST'])

def KinmuPost():
    if not session.get('logged_in'):
        return render_template('login.html',title='ログイン画面')
    else:
        kinmuti  = request.form['kinmu']
        Hourlywage  = request.form['money']
        instartkinmu(kinmuti,Hourlywage)
        return render_template('kinmu.html', title='勤務場所登録')

@app.route('/login')  
def login():
    return render_template('login.html',title='ログイン画面')

@app.route('/login', methods=['POST'])
def login1():
    users  = request.form['id']
    pass1  = request.form['pass']
    userlogin(users,pass1)
    return render_template('login.html',title='ログイン画面')

@app.route('/logout')  
def logout():
    session['logged_in'] = False
    return render_template('login.html',title='ログイン画面')





if __name__ == "__main__":
    # webサーバー立ち上げ
    app.run(debug=True,host="192.168.10.14" ,port=8085)
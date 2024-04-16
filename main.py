import sqlite3

from flask import Flask
from flask import url_for
from flask import request
from flask import render_template
from flask import json
import requests
import random
import os

app = Flask(__name__)


@app.route('/')
def f():
    global zar, voyt, akaynt
    if request.method == 'GET':
        return render_template('osnov1.html', m=zar, n=voyt)


@app.route('/vvod1', methods=['POST', 'GET'])
def vvod1():
    global akaynt
    if request.method == 'GET':
        return render_template('registr.html', m='')
    elif request.method == 'POST':
        i = request.form['name']
        if '@' in request.form['email'] and len(request.form['email']) > 1:
            if len(request.form['name']) > 0 and len(request.form['password']) > 0:
                con = sqlite3.connect('table.db')
                cur = con.cursor()
                cur.execute(
                    """INSERT INTO data(name, email, password) VALUES ( ?, ?, ?)""",
                    (request.form['name'], request.form['email'], request.form['password']))
                con.commit()
                con.close()
                akaynt = True
                nik = i
                return render_template('osnov2.html', m=i)
            else:
                return render_template('registr.html', m='Не все ячейки заполнены')
        else:
            return render_template('registr.html', m='Неправильная почта')


@app.route('/vvod2', methods=['POST', 'GET'])
def vvod2():
    global akaynt
    if request.method == 'GET':
        return render_template('voyti.html', m='')
    elif request.method == 'POST':
        con = sqlite3.connect('table.db')
        cur = con.cursor()
        result = cur.execute("""SELECT * FROM data WHERE email = ? and password = ?""",
                             (request.form['email'], request.form['password'])).fetchone()
        b = result
        con.commit()
        con.close()
        if b == None:
            return render_template('voyti.html', m='Такого аккаунта не существует')
        else:
            akaynt = True
            nik = b[0]
            return render_template('osnov2.html', m=b[0])


@app.route('/posleregistr', methods=['POST', 'GET'])
def posleregistr():
    global nik, voyt
    if request.method == 'GET':
        return render_template('osnov2.html', m=nik)


zar = 'ЗАРЕГИСТРИРОВАТЬСЯ'
voyt = 'ВОЙТИ'
akaynt = False
nik = ''
if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)

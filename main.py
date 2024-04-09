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
    i = 'зарегистрироваться или войти'
    return render_template('index.html', m=i)


@app.route('/vvod', methods=['POST', 'GET'])
def vvod():
    if request.method == 'GET':
        return render_template('registr.html')
    elif request.method == 'POST':
        i = request.form['name']
        return render_template('index.html', m=i)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)

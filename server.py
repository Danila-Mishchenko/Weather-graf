import sqlite3

from flask import Flask
from flask import url_for
from flask import request
import requests
from flask import render_template
from flask import json
import requests
import random
import os

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def f():  # страница до аккаунта
    global zar, voyt, akaynt, temp, feels_like, wind_dir, wind_speed, pressure_mm, humidity, daytime, condition, gorod, lens, kartinki, photo
    if request.method == 'GET':
        return render_template('osnov1.html', m=zar, n=voyt, pr='')
    elif request.method == 'POST':
        if 'search' in request.form:
            search_type = request.form['search']
            a = '0'
            b = '0'
            kop = ''
            api_key = '40d1649f-0493-4b70-98ba-98533de7710b'
            try:  # если поиск неправильный то возникает ошибка
                if search_type == '1':  # нужно чтобы узнать какой поиск производится по координатам или по городам
                    kop = request.form['gorod']
                    ur = f'https://geocode-maps.yandex.ru/1.x/?apikey={api_key}&format=json&geocode={kop}'
                    response21 = requests.get(ur)
                    dat = response21.json()
                    city = dat["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
                    plac = city.split(' ')
                    a = plac[0]
                    b = plac[1]
                elif search_type == '2':
                    i = request.form['search']
                    a = request.form['dolgota']
                    b = request.form['shirota']
                    url = f'https://geocode-maps.yandex.ru/1.x/?apikey={api_key}&format=json&geocode={a},{b}'
                    response2 = requests.get(url)
                    data = response2.json()
                    kop = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
                        'GeocoderMetaData']['Address']['Components'][5]['name']

                access_key = '043f8dde-ac02-4f50-9661-f4941b45341a'  # получаем погоду
                params = {
                    'lat': b,  # широта
                    'lon': a  # долгота
                }
                headers = {
                    'X-Yandex-Weather-Key': access_key
                }

                response = requests.get('https://api.weather.yandex.ru/v2/forecast?', headers=headers, params=params)
                c = response.json()
                temp.insert(0, c["fact"]["temp"])
                feels_like.insert(0, c["fact"]["feels_like"])
                wind_speed.insert(0, c["fact"]["wind_speed"])
                wind_dir.insert(0, napravlenie[c["fact"]["wind_dir"]])
                pressure_mm.insert(0, c["fact"]["pressure_mm"])
                humidity.insert(0, c["fact"]["humidity"])
                daytime.insert(0, sytki[c["fact"]["daytime"]])
                condition.insert(0, weather[c["fact"]["condition"]])
                gorod.insert(0, kop)
                kartinki.insert(0, photo[c["fact"]["condition"]])
                if len(temp) > 6:  # история не больше 6
                    temp = temp[:6]
                    feels_like = feels_like[:6]
                    wind_speed = wind_speed[:6]
                    wind_dir = wind_dir[:6]
                    pressure_mm = pressure_mm[:6]
                    humidity = humidity[:6]
                    daytime = daytime[:6]
                    condition = condition[:6]
                    gorod = gorod[:6]
                lens = []
                for i in range(len(temp)):
                    lens.append(i)  # для удобства в html
                return render_template('osnovpoisk1.html', m=zar, n=voyt, temp=temp, feels_like=feels_like,
                                       wind_dir=wind_dir,
                                       wind_speed=wind_speed, pressure_mm=pressure_mm, humidity=humidity,
                                       daytime=daytime,
                                       condition=condition, city=gorod, dl=lens, probl='', k=kartinki)
            except Exception:
                return render_template('osnovpoisk1.html', m=zar, n=voyt, temp=temp, feels_like=feels_like,
                                       wind_dir=wind_dir,
                                       wind_speed=wind_speed, pressure_mm=pressure_mm, humidity=humidity,
                                       daytime=daytime,
                                       condition=condition, city=gorod, dl=lens,
                                       probl='Не удалось найти попробуйте еще раз', k=kartinki)
        else:
            return render_template('osnov1.html', m=zar, n=voyt, pr='')


@app.route('/vvod1', methods=['POST', 'GET'])
def vvod1():  # страница для регистрации
    global akaynt
    if request.method == 'GET':
        return render_template('registr.html', m='')
    elif request.method == 'POST':
        try:
            i = request.form['name']
            if '@' in request.form['email'] and len(request.form['email']) > 1:  # проверки для корректности
                if len(request.form['name']) > 0 and len(request.form['password']) > 0:
                    con = sqlite3.connect('table.db')  # занос данных в базу
                    cur = con.cursor()
                    cur.execute(
                        """INSERT INTO data(name, email, password) VALUES ( ?, ?, ?)""",
                        (request.form['name'], request.form['email'], request.form['password']))
                    con.commit()
                    con.close()
                    akaynt = True
                    nik = i
                    history = []
                    return posleregistr()
                else:
                    return render_template('registr.html', m='Не все ячейки заполнены')
            else:
                return render_template('registr.html', m='Неправильная почта')
        except Exception:  # нужно чтобы следующие методы post переключались на другую страницу
            history = []
            return posleregistr()


@app.route('/vvod2', methods=['POST', 'GET'])
def vvod2():  # функция для вхождения в аккаунт
    global akaynt, history
    if request.method == 'GET':
        return render_template('voyti.html', m='')
    elif request.method == 'POST':
        try:
            con = sqlite3.connect('table.db')  # проверка на то что есть ли в базе данных
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
                history = []
                return posleregistr()
        except Exception:  # нужно чтобы следующие методы post переключались на другую страницу
            history = []
            return posleregistr()


@app.route('/posleregistr', methods=['POST', 'GET'])
def posleregistr():  # все аналогично как и с функцией до регистрацией но html другой и отсутствуют кнопки регистрации и войти
    global zar, voyt, akaynt, temp, feels_like, wind_dir, wind_speed, pressure_mm, humidity, daytime, condition, gorod, lens, kartinki, photo
    if request.method == 'GET':
        return render_template('osnov2.html', m=nik, n=voyt, pr='')
    elif request.method == 'POST':
        if 'search' in request.form:
            search_type = request.form['search']
            a = '0'
            b = '0'
            kop = ''
            api_key = '40d1649f-0493-4b70-98ba-98533de7710b'
            try:
                if search_type == '1':
                    kop = request.form['gorod']
                    ur = f'https://geocode-maps.yandex.ru/1.x/?apikey={api_key}&format=json&geocode={kop}'
                    response21 = requests.get(ur)
                    dat = response21.json()
                    city = dat["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
                    plac = city.split(' ')
                    a = plac[0]
                    b = plac[1]
                elif search_type == '2':
                    i = request.form['search']
                    a = request.form['dolgota']
                    b = request.form['shirota']
                    url = f'https://geocode-maps.yandex.ru/1.x/?apikey={api_key}&format=json&geocode={a},{b}'
                    response2 = requests.get(url)
                    data = response2.json()
                    kop = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
                        'GeocoderMetaData']['Address']['Components'][5]['name']

                access_key = '043f8dde-ac02-4f50-9661-f4941b45341a'
                params = {
                    'lat': b,  # широта
                    'lon': a  # долгота
                }
                headers = {
                    'X-Yandex-Weather-Key': access_key
                }

                response = requests.get('https://api.weather.yandex.ru/v2/forecast?', headers=headers, params=params)
                c = response.json()
                temp.insert(0, c["fact"]["temp"])
                feels_like.insert(0, c["fact"]["feels_like"])
                wind_speed.insert(0, c["fact"]["wind_speed"])
                wind_dir.insert(0, napravlenie[c["fact"]["wind_dir"]])
                pressure_mm.insert(0, c["fact"]["pressure_mm"])
                humidity.insert(0, c["fact"]["humidity"])
                daytime.insert(0, sytki[c["fact"]["daytime"]])
                condition.insert(0, weather[c["fact"]["condition"]])
                gorod.insert(0, kop)
                kartinki.insert(0, photo[c["fact"]["condition"]])
                if len(temp) > 6:
                    temp = temp[:6]
                    feels_like = feels_like[:6]
                    wind_speed = wind_speed[:6]
                    wind_dir = wind_dir[:6]
                    pressure_mm = pressure_mm[:6]
                    humidity = humidity[:6]
                    daytime = daytime[:6]
                    condition = condition[:6]
                    gorod = gorod[:6]
                lens = []
                for i in range(len(temp)):
                    lens.append(i)
                return render_template('osnovpoisk2.html', m=nik, n=voyt, temp=temp, feels_like=feels_like,
                                       wind_dir=wind_dir,
                                       wind_speed=wind_speed, pressure_mm=pressure_mm, humidity=humidity,
                                       daytime=daytime,
                                       condition=condition, city=gorod, dl=lens, probl='', k=kartinki)
            except Exception:
                return render_template('osnovpoisk2.html', m=nik, n=voyt, temp=temp, feels_like=feels_like,
                                       wind_dir=wind_dir,
                                       wind_speed=wind_speed, pressure_mm=pressure_mm, humidity=humidity,
                                       daytime=daytime,
                                       condition=condition, city=gorod, dl=lens,
                                       probl='Не удалось найти попробуйте еще раз', k=kartinki)
        else:
            return render_template('osnov2.html', m=zar, n=voyt, pr='')


@app.route('/podrob/<nazv>')
def podrob(nazv): # подробная информация прогноза погоды
    api_key = '40d1649f-0493-4b70-98ba-98533de7710b'
    ur = f'https://geocode-maps.yandex.ru/1.x/?apikey={api_key}&format=json&geocode={nazv}'
    response21 = requests.get(ur)
    dat = response21.json()
    city = dat["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
    plac = city.split(' ')
    a = plac[0]
    b = plac[1]
    access_key = '043f8dde-ac02-4f50-9661-f4941b45341a'
    params = {
        'lat': b,  # широта
        'lon': a  # долгота
    }
    headers = {
        'X-Yandex-Weather-Key': access_key
    }

    response = requests.get('https://api.weather.yandex.ru/v2/forecast?', headers=headers, params=params)
    c = response.json()
    spisok1 = [] # списки для информации почасовой на следующие три дня
    spisok2 = []
    spisok3 = []
    spisok1.append('Дата: ' + c["forecasts"][0]["date"])
    spisok2.append('Дата: ' + c["forecasts"][1]["date"])
    spisok3.append('Дата: ' + c["forecasts"][2]["date"])
    for i in range(24):
        spisok1.append('________')
        spisok1.append('Время ' + c["forecasts"][0]["hours"][i]["hour"] + ':00')
        spisok1.append('Температура: ' + str(c["forecasts"][0]["hours"][i]["temp"]) + '°C')
        spisok1.append('Погода: ' + weather[c["forecasts"][0]["hours"][i]["condition"]])
        spisok1.append('Скорость ветра: ' + str(c["forecasts"][0]["hours"][i]["wind_speed"]) + 'м/с')
    for i in range(24):
        spisok2.append('________')
        spisok2.append('Время ' + c["forecasts"][1]["hours"][i]["hour"] + ':00')
        spisok2.append('Температура: ' + str(c["forecasts"][1]["hours"][i]["temp"]) + '°C')
        spisok2.append('Погода: ' + weather[c["forecasts"][1]["hours"][i]["condition"]])
        spisok2.append('Скорость ветра: ' + str(c["forecasts"][1]["hours"][i]["wind_speed"]) + 'м/с')
    for i in range(24):
        spisok3.append('________')
        spisok3.append('Время ' + c["forecasts"][2]["hours"][i]["hour"] + ':00')
        spisok3.append('Температура: ' + str(c["forecasts"][2]["hours"][i]["temp"]) + '°C')
        spisok3.append('Погода: ' + weather[c["forecasts"][2]["hours"][i]["condition"]])
        spisok3.append('Скорость ветра: ' + str(c["forecasts"][2]["hours"][i]["wind_speed"]) + 'м/с')
    return render_template('podrob.html', sp1=spisok1, sp2=spisok2, sp3=spisok3)


zar = 'ЗАРЕГИСТРИРОВАТЬСЯ'
voyt = 'ВОЙТИ'
akaynt = False
nik = ''
gorod = []  # список городов
history = []  # история поиска
temp = []  # температура
feels_like = []  # ощущается
wind_speed = []  # скорость ветра
wind_dir = []  # направление ветра
pressure_mm = []  # давление
humidity = []  # влажность
daytime = []  # время суток
condition = []  # погода
lens = []  # длина - нужна для индексов в html
kartinki = []  # список для картинок
sytki = {  # перевод
    "d": 'день',
    "n": 'ночь'
}
weather = {  # перевод
    "clear": 'ясно',
    "partly-cloudy": 'малооблачно',
    "cloudy": 'облачно с прояснениями',
    "overcast": 'пасмурно',
    "light-rain": 'небольшой дождь',
    "rain": 'дождь',
    "heavy-rain": 'сильный дождь',
    "showers": 'ливень',
    "wet-snow": 'дождь со снегом',
    "light-snow": 'небольшой снег',
    "snow": 'снег',
    "snow-showers": 'снегопад',
    "hail": 'град',
    "thunderstorm": 'гроза',
    "thunderstorm-with-rain": 'дождь с грозой',
    "thunderstorm-with-hail": 'гроза с градом'
}
photo = {  # чтобы подбирать картинки
    "clear": '/static/img/sunny.svg',
    "partly-cloudy": '/static/img/cloudy.svg',
    "cloudy": '/static/img/cloudy.svg',
    "overcast": '/static/img/foggy.svg',
    "light-rain": '/static/img/rain-day.svg',
    "rain": '/static/img/rain-day.svg',
    "heavy-rain": '/static/img/rain-day.svg',
    "showers": '/static/img/rain-day.svg',
    "wet-snow": '/static/img/Snow.svg',
    "light-snow": '/static/img/Snow.svg',
    "snow": '/static/img/Snow.svg',
    "snow-showers": '/static/img/Snow.svg',
    "hail": '/static/img/Snow.svg',
    "thunderstorm": '/static/img/storm.svg',
    "thunderstorm-with-rain": '/static/img/storm.svg',
    "thunderstorm-with-hail": '/static/img/storm.svg'
}
napravlenie = {
    "nw": 'северо-западное',
    "n": 'северное',
    "ne": 'северо-восточное',
    "e": 'восточное',
    "se": 'юго-восточное',
    "s": 'южное',
    "sw": 'юго-западное',
    "w": 'западное',
    "c": 'штиль',
}
if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)

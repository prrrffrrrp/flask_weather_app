import requests
from config import Config
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


app = Flask(__name__)
app.config.from_object(Config)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


class CityForm(FlaskForm):
    city = StringField('city', validators=[DataRequired()])


@app.route('/', methods=['GET', 'POST'])
def index():
    form = CityForm()
    if form.validate_on_submit():
        existing_city = City.query.filter_by(name=form.city.data).first()

        if existing_city:
            flash("This city is already in the database")
        else:
            new_city_obj = City(name=form.city.data)
            db.session.add(new_city_obj)
            db.session.commit()

    weather_data = []
    cities = City.query.all()
    for city in cities:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city.name}&units=metric&appid={app.config['WEATHER_API_KEY']}"

        r = requests.get(url).json()

        weather = {
            'city': city.name,
            'temperature': r['main']['temp'],
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon'],
        }
        weather_data.append(weather)

    return render_template('index.html', weather_data=weather_data, form=CityForm())


@app.route('/city/<string:city_name>')
def city(city_name):

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&appid={app.config['WEATHER_API_KEY']}"
    r = requests.get(url).json()

    city_weather = {
        'city': city_name,
        'temperature': r['main']['temp'],
        'temp_min': r['main']['temp_min'],
        'temp_max': r['main']['temp_max'],
        'pressure': r['main']['pressure'],
        'humidity': r['main']['humidity'],
        'feels_like': r['main']['feels_like'],
        'description': r['weather'][0]['description'],
        'icon': r['weather'][0]['icon'],
    }
    return render_template('city.html', city_weather=city_weather)


@app.route('/city/<string:city_name>/delete', methods=['POST'])
def delete_city(city_name):
    city_obj = City.query.filter_by(name=city_name).first()
    db.session.delete(city_obj)
    db.session.commit()

    return redirect(url_for('index'))

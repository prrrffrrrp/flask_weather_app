import requests
from config import Config
from flask import Flask, render_template, flash
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

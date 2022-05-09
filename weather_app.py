from flask_weather_app.app import app, City, db


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'City': City}

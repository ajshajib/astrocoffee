from flask import Flask

app = Flask(__name__, instance_relative_config=True)


@app.route('/')
def index():
    return 'AstroCoffee is brewing!'

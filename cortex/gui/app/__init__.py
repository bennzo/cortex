import time
from flask import Flask, render_template, url_for


app = Flask(__name__,
            static_folder='static',
            template_folder='templates')


@app.route('/time')
def get_current_time():
    return {'time': time.time()}


@app.route('/')
def index():
    api_host, api_port = app.config['API_HOST'], app.config['API_PORT']
    return render_template("index.html", api_host=api_host, api_port=api_port)

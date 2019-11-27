import logging
import time

import sh
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

app.config.from_mapping(
    SECRET_KEY='dev',
)

socketio = SocketIO(app)

tail = None

frontier_size = None
top_10 = None
current_job = None
previous_job = None
current_iteration_count = None


@app.route('/')
def status():
    return render_template('index.html')


@app.route('/')
def index():
    """Serve the index HTML"""
    return render_template('index.html')


def status_update(line):
    global frontier_size, current_job, previous_job, current_iteration_count
    if 'monitoring' in line:
        frontier_size = line
    if 'done with Job' in line:
        previous_job = line

    if '----> Checking' in line:
        current_iteration_count = line

    if 'running for Job' in line:
        current_job = line


@socketio.on('status')
def status():
    while True:
        emit('status', [frontier_size, current_iteration_count, previous_job, current_job])
        time.sleep(1)


@socketio.on('log')
def log():
    global tail
    tail = sh.tail("-f", "-n", "2000",
                   "/Users/yicong/Library/Mobile Documents/com~apple~CloudDocs/Research/TwiSpider/nohup.out",
                   _iter=True)
    while True:
        log = tail.next()
        if log:
            status_update(log)
            emit('log', log)


if __name__ == '__main__':
    from argparse import ArgumentParser
    from waitress import serve

    parser = ArgumentParser()
    parser.add_argument("--deploy", help="deploy server in production mode",
                        action="store_true")
    args = parser.parse_args()
    if args.deploy:
        serve(app, host='0.0.0.0', port=2333)
    else:
        socketio.run(app, port=5000, debug=True)

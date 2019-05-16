import socket
from flask import Flask

app = Flask(__name__)

VERSION = "0.2.0"

@app.route('/')
def index():
    message = socket.gethostname()
    template = "I'm " + message
    return template

@app.route('/health')
def health():
    return '200'

@app.route('/version')
def version():
    return VERSION

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
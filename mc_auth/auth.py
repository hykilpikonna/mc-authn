import _thread
import os
import time
import urllib.parse
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import StringIO
from threading import Thread

import uvicorn
from fastapi import FastAPI
from ruamel import yaml


def load_config() -> dict:
    with open('auth_config.yml') as f:
        yml = yaml.safe_load(f)
    return yml


config = load_config()


def get_login_code() -> str:
    app = FastAPI()
    result = {}

    @app.get('/')
    def callback(code: str):
        print('Login code received!')
        result['code'] = code
        return 'Login success!'

    def run():
        uvicorn.run(app, host="0.0.0.0", port=18275, reload=False)

    th = Thread(target=run)
    th.start()

    # Open url in browser
    url = "https://login.live.com/oauth20_authorize.srf?"
    url += urllib.parse.urlencode({
        'client_id': config['ClientID'],
        'response_type': 'code',
        'redirect_uri': 'http://localhost:18275',
        'scope': 'XboxLive.signin offline_access',
        'state': 'NOT_NEEDED'
    })
    webbrowser.open(url)

    while 'code' not in result:
        time.sleep(0.01)

    return result['code']


if __name__ == '__main__':
    print(get_login_code())

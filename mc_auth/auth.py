import time
import time
import urllib.parse
import webbrowser
from pathlib import Path
from threading import Thread

import requests
import uvicorn
from fastapi import FastAPI
from hypy_utils import ensure_dir, write, json_stringify
from ruamel import yaml

config_path = ensure_dir(Path.home() / '.config' / 'mc-auth')


def load_config() -> dict:
    auth_config = config_path / 'auth_config.yml'

    if not auth_config.is_file():
        print(f'Cannot find {auth_config}, please put your config file there.')
        exit(127)

    with (config_path / 'auth_config.yml').open(encoding='utf-8') as f:
        yml = yaml.safe_load(f)

    return yml


config = load_config()
http = requests.Session()


def get_login_code() -> str:
    app = FastAPI()
    result = {}

    @app.get('/')
    def callback(code: str):
        print('Login code received!')
        result['code'] = code
        return 'Login success! You can close this window now.'

    def run():
        uvicorn.run(app, host="0.0.0.0", port=18275, reload=False)

    th = Thread(target=run)
    th.setDaemon(True)
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


def get_access_token(login_code: str) -> str:
    print('Getting access token with login code...')
    out_path = config_path / 'debug' / 'access_token.json'

    r = http.post("https://login.live.com/oauth20_token.srf", data={
        'client_id': config['ClientID'],
        'client_secret': config['ClientSecret'],
        'code': login_code,
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://localhost:18275'
    }).json()

    write(out_path, json_stringify(r, indent=2))
    print(f'> Success! Response saved to {out_path}')

    return r['access_token']


def get_xbox_live_token(token: str) -> str:
    print('Logging into Xbox Live with access token...')
    out_path = config_path / 'debug' / 'xbox_live_token.json'

    r = http.post('https://user.auth.xboxlive.com/user/authenticate', json={
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": 'd=' + token
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT"
    }, headers={'Accept': 'application/json', 'Content-Type': 'application/json'}).json()

    write(out_path, json_stringify(r, indent=2))
    print(f'> Success! Response saved to {out_path}')

    return r['Token']


def get_mc_token(token: str) -> str:
    print('Logging into Minecraft with Xbox Live token...')
    out_path = config_path / 'debug' / 'mc_token.json'

    r = http.post('https://xsts.auth.xboxlive.com/xsts/authorize', json={
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [token]
        },
        "RelyingParty": "rp://api.minecraftservices.com/",
        "TokenType": "JWT"
    }).json()

    write(out_path, json_stringify(r, indent=2))
    print(f'> Success! Response saved to {out_path}')

    return r['Token']


if __name__ == '__main__':
    code = get_login_code()
    t1 = get_access_token(code)
    t2 = get_xbox_live_token(t1)
    t3 = get_mc_token(t2)
    print(f'Your token is {t3}')

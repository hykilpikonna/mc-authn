from __future__ import annotations

import json
import time
import time
import urllib.parse
import webbrowser
from pathlib import Path
from threading import Thread

import requests
import uvicorn
from fastapi import FastAPI
from hypy_utils import ensure_dir, write, json_stringify, printc, color
from ruamel import yaml

__version__ = "1.0.2"
config_path = ensure_dir(Path.home() / '.config' / 'mc-auth')
access_token_path = config_path / 'data' / 'access_token.json'


def load_config() -> dict:
    auth_config = config_path / 'auth_config.yml'

    if not auth_config.is_file():
        printc(f'&cCannot find config {auth_config}\n'
               f'&6Please read https://github.com/hykilpikonna/mc-authn for setup instructions.')
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
        uvicorn.run(app, host="0.0.0.0", port=18275, reload=False, log_level='error')

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
    print(f'&6Opening {url} in the browser...')
    if webbrowser.open(url):
        print(f'&6If the link does not open, please open it manually.')
    else:
        print(f'&cFailed to open the link automatically, please open it manually.')

    while 'code' not in result:
        time.sleep(0.01)

    return result['code']


def get_access_token(login_code: str) -> str:
    printc('&6Getting access token with login code...')

    r = http.post("https://login.live.com/oauth20_token.srf", data={
        'client_id': config['ClientID'],
        'client_secret': config['ClientSecret'],
        'code': login_code,
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://localhost:18275'
    }).json()

    write(access_token_path, json_stringify(r, indent=2))
    assert 'access_token' in r, color('&c> Request failed. Token is not in the response.')
    printc(f'&a> Success! Response saved to {access_token_path}')

    return r['access_token']


def get_refresh_token() -> str | None:
    if not access_token_path.is_file():
        return None
    j: dict = json.loads(access_token_path.read_text('utf-8'))
    return j.get('refresh_token')


def refresh_access_token(refresh_token: str) -> str:
    printc('&6Refreshing access token with refresh token...')

    r = http.post("https://login.live.com/oauth20_token.srf", data={
        'client_id': config['ClientID'],
        'client_secret': config['ClientSecret'],
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
        'redirect_uri': 'http://localhost:18275'
    }).json()

    write(access_token_path, json_stringify(r, indent=2))
    assert 'access_token' in r, color('&c> Request failed. Token is not in the response.')
    printc(f'&a> Success! Response saved to {access_token_path}')

    return r['access_token']


def get_xbox_live_token(token: str) -> str:
    printc('&6Logging into Xbox Live with access token...')
    out_path = config_path / 'debug' / 'xbox_live_token.json'

    r = http.post('https://user.auth.xboxlive.com/user/authenticate', json={
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": 'd=' + token
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT"
    }).json()

    write(out_path, json_stringify(r, indent=2))
    assert 'Token' in r, color('&c> Request failed. Token is not in the response.')
    printc(f'&a> Success! Response saved to {out_path}')

    return r['Token']


def get_xsts_token(token: str) -> tuple[str, str]:
    """
    :return: token, user hash
    """
    printc('&6Logging into XSTS with Xbox Live token...')
    out_path = config_path / 'debug' / 'xsts_token.json'

    r = http.post('https://xsts.auth.xboxlive.com/xsts/authorize', json={
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [token]
        },
        "RelyingParty": "rp://api.minecraftservices.com/",
        "TokenType": "JWT"
    }).json()

    write(out_path, json_stringify(r, indent=2))
    assert 'Token' in r, color('&c> Request failed. Token is not in the response.')
    printc(f'&a> Success! Response saved to {out_path}')

    return r['Token'], r['DisplayClaims']['xui'][0]['uhs']


def get_mc_token(xsts_token: str, user_hash: str) -> str:
    printc('&6Logging into Minecraft with XSTS token...')
    out_path = config_path / 'debug' / 'mc_token.json'

    r = http.post('https://api.minecraftservices.com/authentication/login_with_xbox', json={
        "identityToken": f"XBL3.0 x={user_hash};{xsts_token}",
        "ensureLegacyEnabled": True
    }).json()

    write(out_path, json_stringify(r, indent=2))
    printc(f'&a> Success! Response saved to {out_path}')

    mc_token = config_path / 'mc-token.txt'
    write(mc_token, r['access_token'])
    printc(f'&a> Minecraft token saved to {mc_token}')

    return r['access_token']


def full_login():
    printc(f'&3mc-authn {__version__} by HyDEV')
    print()

    refresh_token = get_refresh_token()
    if refresh_token:
        t1 = refresh_access_token(refresh_token)
        print()
    else:
        code = get_login_code()
        print()
        t1 = get_access_token(code)
        print()

    t2 = get_xbox_live_token(t1)
    print()
    t3, uhs = get_xsts_token(t2)
    print()
    t4 = get_mc_token(t3, uhs)


if __name__ == '__main__':
    full_login()

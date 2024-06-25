import hashlib
import json
import random
import string
import base64
from fake_useragent import UserAgent
from bot.config import settings
from jwt import InvalidTokenError,decode
from time import time
from urllib.parse import quote

def generate_random_visitor_id():
    random_string = ''.join(
        random.choices(string.ascii_letters + string.digits, k=32)
    )
    visitor_id = hashlib.md5(random_string.encode()).hexdigest()

    return visitor_id


def escape_html(text: str) -> str:
    return text.replace('<', '\\<').replace('>', '\\>')


def decode_cipher(cipher: str) -> str:
    encoded = cipher[:3] + cipher[4:]
    return base64.b64decode(encoded).decode('utf-8')


def get_mobile_user_agent() -> str:
    """
    Function: get_mobile_user_agent

    This method generates a random mobile user agent for an Android platform.
    If the generated user agent does not contain the "wv" string,
    it adds it to the browser version component.

    :return: A random mobile user agent for Android platform.
    """
    ua = UserAgent(platforms=['mobile'], os=['android'])
    user_agent = ua.random
    if 'wv' not in user_agent:
        parts = user_agent.split(')')
        parts[0] += '; wv'
        user_agent = ')'.join(parts)
    return user_agent


def get_headers(name: str):
    try:
        with open('profile.json', 'r') as file:
            profile = json.load(file)
    except:
        profile = {}

    headers = profile.get(name, {}).get('headers', {})

    if settings.USE_RANDOM_USERAGENT:
        android_version = random.randint(24, 33)
        webview_version = random.randint(70, 125)

        headers['Sec-Ch-Ua'] = (
            f'"Android WebView";v="{webview_version}", '
            f'"Chromium";v="{webview_version}", '
            f'"Not?A_Brand";v="{android_version}"'
        )
        headers['User-Agent'] = get_mobile_user_agent()

    return headers

def is_jwt_valid(token: str) -> bool:
    try:
        decoded = decode(token, options={"verify_signature": False})
        if int(decoded['exp']) < (int(time()) - 50):
            return False
        else:
            return True
    except InvalidTokenError:
        return False

def convert_to_url_encoded_format(input_string: str):
    parts = input_string.split('&')
    encoded_parts = []
    for part in parts:
        key, value = part.split('=', 1)
        if key == 'user':
            value = quote(value)
        encoded_parts.append(f"{key}={value}")
    return '&'.join(encoded_parts)
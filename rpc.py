from itsdangerous import Serializer
from werkzeug.http import parse_cookie
from uwsgidecorators import rpc
import os

SECRET_KEY = os.environ['SECRET_KEY']
AUTH_COOKIE = os.environ['AUTH_COOKIE']

# make sure rpc retuns at least something, an empty string breaks uwsgi routing
# also it should return bytes on python3

@rpc('authrpc')
def authrpc(http_cookie):
    cookies = parse_cookie(http_cookie)
    cookie = cookies.get(AUTH_COOKIE)
    if cookie is None:
        return b'no cookie'
    s = Serializer(SECRET_KEY)
    payload = s.loads(cookie)
    if payload.get('authorized') == True:
       return b'OK'
    return b'no authorization'

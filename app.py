from flask import Flask, Response, request, render_template, \
        session, flash, redirect, url_for, escape
from itsdangerous import Serializer
import qrcode
import pyotp
import io
import os

# built in user so that I don't have to recreate it every time :)
db = {'gdamjan@totp':'7MSXJKXUTCLYOS4J'}

app = Flask(__name__)
app.debug = True

SECRET_KEY = os.environ['SECRET_KEY']
AUTH_COOKIE = os.environ['AUTH_COOKIE']
app.secret_key = SECRET_KEY

@app.route('/', methods=['GET'])
def login():
    url = session['url'] = request.args.get('url', '/')
    return render_template('login.html', url=url)

@app.route('/', methods=['POST'])
def do_login():
    user = request.form.get('user')
    token = request.form.get('token')

    secret = db.get(user)
    if not secret:
        flash('user unknown')
        return redirect(url_for('login'))
    totp = pyotp.TOTP(secret)
    if totp.verify(token):
        print("Login success")
        url = session.pop('url', '/')
        response = redirect(url)
        s = Serializer(SECRET_KEY)
        cookie = s.dumps({'authorized':True})
        response.set_cookie(AUTH_COOKIE, cookie)
        return response
    else:
        flash("totp didn't verify")
        return redirect(url_for('login'))

@app.route('/new/', methods=['POST', 'GET'])
def confirm():
    user = request.values.get('user')
    if user is None:
        return render_template('new.html')
    session['user'] = user

    secret = session.get('secret')
    if secret is None:
        secret = pyotp.random_base32()
        session['secret'] = secret

    totp = pyotp.TOTP(secret)
    provision = totp.provisioning_uri(user)
    return render_template('confirm.html', provision=provision)

@app.route('/new/qrcode.png', methods=['GET'])
def qrcodeimg():
    user = session['user']
    secret = session['secret']
    totp = pyotp.TOTP(secret)
    provision = totp.provisioning_uri(user)
    # ^ session or url argument?
    img = qrcode.make(provision)
    img_io = io.BytesIO()
    img.save(img_io)
    response = Response(img_io.getvalue(), mimetype='image/png')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/new/create', methods=['POST'])
def create():
    user = session.get('user')
    secret = session.get('secret')
    token = request.form.get('token')
    totp = pyotp.TOTP(secret)
    if totp.verify(token):
        db[user] = secret
        flash('User created!')
        session.pop('user')
        session.pop('secret')
        return redirect(url_for('login'))
    else:
        flash('Token not confirmed')
        return redirect(url_for('confirm', user=user))

@app.route('/logout', methods=['GET'])
def logout():
    return render_template('logout.html')

@app.route('/logout', methods=['POST'])
def do_logout():
    response = redirect(url_for('login'))
    response.delete_cookie(AUTH_COOKIE)
    session.clear()
    flash('Logged out!')
    return response

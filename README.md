# Demo flask auth app using pyotp, qrcode to authenticate uwsgi proxy

## OTP auth app

The flask app (at the `/_auth` path) allows users to login with a username and a TOTP token,
to logout (clears the session and cookies) and to setup their user and token. Before the user is created
they must confirm they've setup theirs TOTP app correctly by entering a valid token.

Users and their OTP secrets are stored in a runtime dictionary for this demo. In a more serious
application they would be stored in a database, and passwords would be used too.

## uwsgi proxy, routing and rpc

uwsgi can act as a http proxy (but not https) to other services. My idea was to only allow the proxy for
authorized users. Using uwsgi internal routing a rpc call is made to a python function that checks for a
secure cookie. If the secure cookie is not present, or it doesn't contain proper authorization, the request
is redirected to `/_auth` where the user can authenticate. The above python app needs to set the secure cookie.

A rpc call is made for each proxied request, but the proxying itself is made by the uwsgi offloading infrastructure.

The upstream server is configured in the uwsgi config file (see upstream in `auth.ini`).

## Leaking of the cookie

The secure cookie is based on `itsdangerous`, it can't be tampered with nor created without the knowledge of the
app global secret key, since it's cryptographically signed. But the cookie is authorization equivalent.

The secure cookie will leak to the proxied service, thus this setup is not recommended to proxy to 3rd party services
(the benefits of that are also questionable). Maybe uwsgi will get the option to remove the cookie in a routing action.

Anyway the real application of this solution is proxying to internal services that don't have good enough (or at all)
authentification support. Possible additions can be OAuth authentification and also adding access permissions in the
cookie and rpc.

## Python 3

All of this is tested and works on python 3.5.1. It will probably work on >=2.7 and 3.4 or so. The `pip` and
`python` commands are python 3.x here (on ArchLinux).

## Install and run

I typically use uwsgi installed from distro packages. Needed features are routing, python plugin,
and optinally the cares plugin to specify the destination host by name, and not by address.

```
export PYTHONUSERBASE=$PWD/py-env
pip install --user -r requirements.txt
uwsgi --ini auth.ini
```

## References

* [uwsgi routing](http://uwsgi-docs.readthedocs.org/en/latest/InternalRouting.html)
* [uwsgi rpc](http://uwsgi-docs.readthedocs.org/en/latest/RPC.html)
* [itsdangerous](http://pythonhosted.org/itsdangerous/)
* [qrcode](https://pypi.python.org/pypi/qrcode)
* [pyotp](https://pyotp.readthedocs.org)
* [Flask](http://flask.pocoo.org/)

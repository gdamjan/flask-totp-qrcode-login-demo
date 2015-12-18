# Demo flask app using pyotp, qrcode + uwsgi proxy and rpc

## OTP auth app

The flask app (siting on the `/_auth` path) allows users to login with a username and a TOTP token,
to logout (clears the session) and setup their user and token. Before the user is created they must
confirm they setup his TOTP app corectly by entering the valid token.

Users and their OTP secrets are stored in a runtime dictionary for the demo.

The session is the default secure cookie based client side session from flask.

## uwsgi proxy, routing and rpc

uwsgi can act as a http proxy (but not https) to other services. My idea was to only allow the proxy for
authorized users. Using uwsgi internal routing a rpc call is made to a python function that checks for a
secure cookie. If the secure cookie is not present, or it doesn't contain proper authorization, the request
is redirected to `/_auth` where the user can authenticate. The above python app needs to set the secure cookie.

a rpc call is made for each proxied request, but the proxing itself is made by the uwsgi offloading infrastructure.

## Leaking of the cookie

The secure cookie will leak to the proxied service, thus this setup is not recommended to proxy to 3rd party services
(the benefits of that are also questionable). Maybe uwsgi will get the option to remove the cookie in a routing action.

Anyway the real application of this solution is proxing to internal services that don't have good enough (or at all)
auth support.

## References

* [uwsgi routing](http://uwsgi-docs.readthedocs.org/en/latest/InternalRouting.html)
* [uwsgi rpc](http://uwsgi-docs.readthedocs.org/en/latest/RPC.html)
* [secure cookie](http://werkzeug.pocoo.org/docs/0.11/contrib/securecookie/)
* [qrcode](https://pypi.python.org/pypi/qrcode)
* [pyotp](https://pyotp.readthedocs.org)
* [Flask](http://flask.pocoo.org/)

#!/usr/bin/env python
# coding: utf-8


# In[1]:


import json
import logging

from flask import Flask, g
from flask_oidc import OpenIDConnect
import requests

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config.update({
    'SECRET_KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIwZWNmMmI0YS00ZDkwLTQ0MDktOGNiZC1mZGM4NWFiZjYyOWUifQ.eyJleHAiOjE2Njk2NzQ5NTAsImlhdCI6MTY2OTU4ODU1MCwianRpIjoiOGU1MjNiNzQtODAxMS00ZmRlLTk0MWMtM2IwMTcwYWJiMzRkIiwiaXNzIjoiaHR0cDovL2xvY2FsaG9zdDozMDAwL3JlYWxtcy90cmlhbCIsImF1ZCI6Imh0dHA6Ly9sb2NhbGhvc3Q6MzAwMC9yZWFsbXMvdHJpYWwiLCJ0eXAiOiJJbml0aWFsQWNjZXNzVG9rZW4ifQ.zTBY9sPlMDWWbdXzL_jStqZYVTlpFEhwRN2gWEE2EHc'
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_OPENID_REALM': 'trial',
    'OIDC_SCOPES': ['openid', 'email', 'profile'],
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post'
})

oidc = OpenIDConnect(app)


@app.route('/')
def hello_world():
    if oidc.user_loggedin:
        return ('Hello, %s, <a href="/private">See private</a> '
                '<a href="/logout">Log out</a>') % \
            oidc.user_getfield('username')
    else:
        return 'Welcome please register, <a href="/private">Log in</a>'


@app.route('/private')
@oidc.require_login
def hello():
    info = oidc.user_getinfo(['username', 'email', 'sub'])

    username = info.get('username')
    email = info.get('email')
    user_id = info.get('sub')

    if user_id in oidc.credentials_store:
        try:
            from oauth2client.client import OAuth2Credentials
            access_token = OAuth2Credentials.from_json(oidc.credentials_store[user_id]).access_token
            print ('access_token=<%s>' % access_token)
            headers = {'Authorization': 'Bearer %s' % (access_token)}
            # YOLO
            greeting = requests.get('http://localhost:8080/greeting', headers=headers).text
        except:
            print ("Bad request")
            greeting = "Hello %s" % username
    

    return ("""%s your email is %s and your user_id is %s!
               <ul>
                 <li><a href="/">Home</a></li>
                 <li><a href="//localhost:8081/auth/realms/pysaar/account?referrer=flask-app&referrer_uri=http://localhost:5000/private&">Account</a></li>
                </ul>""" %
            (greeting, email, user_id))


@app.route('/api', methods=['POST'])
@oidc.accept_token(require_token=True, scopes_required=['openid'])
def hello_api():

    return json.dumps({'hello': 'Welcome %s' % g.oidc_token_info['sub']})


@app.route('/logout')
def logout():
    
    oidc.logout()
    return 'Hi, you have been logged out! <a href="/">Return</a>'


if __name__ == '__main__':
    app.run()


# In[ ]:





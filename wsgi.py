#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import requests
import argparse
import traceback
from flask import Flask, request, redirect, Response, make_response, abort

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', help='Username', default=os.getenv('PEERTUBE_USERNAME', ''))
parser.add_argument('-p', '--password', help='Password', default=os.getenv('PEERTUBE_PASSWORD', 'password'))
parser.add_argument('-c', '--client_id', help='Channel ID to use', default=os.getenv('PEERTUBE_CLIENT_ID', 'client_id'))
parser.add_argument('-s', '--client_secret', help='Client secret to use', default=os.getenv('PEERTUBE_CLIENT_SECRET', 'client_secret'))
parser.add_argument('-e', '--endpoint', help='Peertube endpoint', default=os.getenv('PEERTUBE_ENDPOINT', 'http://localhost:9000'))
parser.add_argument('-H', '--host', help='Host to listen on', default=os.getenv('LISTEN_HOST', 'localhost'))
parser.add_argument('-P', '--port', help='Port', default=os.getenv('LISTEN_PORT', '9001'))
parser.add_argument('--nowebtorrent', help='Disable webTorrent', default=bool(os.getenv('PEERTUBE_DISABLE_WEBTORRENT', 'False')))
args = parser.parse_args()
application = Flask(__name__)

@application.route('/favicon.ico')
def favicon():
    return abort(404)

@application.route('/', defaults={'path': ''})
@application.route('/<path:path>')
def root(path):
    auth_data = {'client_id': args.client_id,
                'client_secret': args.client_secret,
                'grant_type': 'password',
                'password': args.password,
                'response_type': 'code',
                'username': request.headers.get('X-User').lower() if 'X-User' in request.headers else args.username
                }
    auth_result = requests.post('{0}{1}'.format(args.endpoint, '/api/v1/users/token'), data=auth_data)
    if auth_result.status_code == 400 and auth_result.json()['code'] == 'invalid_grant':
        registration_data = {'email': request.headers.get('X-Email') if 'X-Email' in request.headers else '{0}@nfa.cz'.format(args.username),
                             'password': args.password,
                             'terms': 'true',
                             'username': request.headers.get('X-User').lower() if 'X-User' in request.headers else args.username}
        user_registration = requests.post('{0}{1}'.format(args.endpoint, '/api/v1/users/register'), data=registration_data)
        if not user_registration.status_code == 204:
            return(user_registration.text, user_registration.status_code)
        else:
            return(redirect('/{0}'.format(path)))
    elif not auth_result.status_code == 200:
        return(auth_result.text, auth_result.status_code)
    else:
        data = auth_result.json()

    try:
        access_token = (data['access_token'])
        auth_headers = {'Authorization': 'Bearer {0}'.format(access_token)}
        user_info = requests.get('{0}{1}'.format(args.endpoint, '/api/v1/users/me'), headers=auth_headers).json()

        if args.nowebtorrent and user_info['webTorrentEnabled'] == True:
            user_modify = requests.put('{0}{1}'.format(args.endpoint, '/api/v1/users/me'), headers=auth_headers, data={'webTorrentEnabled': "false"})
            if not user_modify.status_code == 204: return(user_modify.text, user_modify.status_code)

        refresh_token = (data['refresh_token'])
        token_type = (data['token_type'])
        local_storage_data = ['localStorage.setItem("access_token", "{0}");'.format(access_token),
                              'localStorage.setItem("refresh_token", "{0}");'.format(refresh_token),
                              'localStorage.setItem("token_type", "{0}");'.format(token_type),
                              'localStorage.setItem("id", "{0}");'.format(user_info['id']),
                              'localStorage.setItem("role", "{0}");'.format(user_info['role']),
                              'localStorage.setItem("email", "{0}");'.format(user_info['email']),
                              'localStorage.setItem("username", "{0}");'.format(user_info['username'])]
        local_storage_data = ''.join(local_storage_data)
        response = make_response('<script>{0};window.location.href = "/{1}";</script>'.format(local_storage_data, path))
        response.set_cookie('peertube_auth', 'yes')
        return response
    except KeyError:
        return Response(auth_result.text, 401)
    except Exception as err:
        traceback.print_exc()
        return Response('Error during login', 500)


if __name__ == '__main__':
     application.run(threaded=True, host=args.host, port=int(args.port))


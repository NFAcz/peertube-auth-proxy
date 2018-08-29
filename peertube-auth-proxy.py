#!/usr/bin/env python
from __future__ import print_function
import os
import sys
import requests
import argparse
from flask import Flask, request, redirect, Response, make_response

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', help='Username', default=os.getenv('PEERTUBE_USERNAME', ''))
parser.add_argument('-p', '--password', help='Password', default=os.getenv('PEERTUBE_PASSWORD', 'password'))
parser.add_argument('-c', '--client_id', help='Channel ID to use', default=os.getenv('PEERTUBE_CLIENT_ID', 'client_id'))
parser.add_argument('-s', '--client_secret', help='Client secret to use', default=os.getenv('PEERTUBE_CLIENT_SECRET', 'client_secret'))
parser.add_argument('-e', '--endpoint', help='Peertube endpoint', default=os.getenv('PEERTUBE_ENDPOINT', 'http://localhost:9000'))
parser.add_argument('-H', '--host', help='Host to listen on', default=os.getenv('LISTEN_HOST', 'localhost'))
parser.add_argument('-P', '--port', help='Port', default=os.getenv('LISTEN_PORT', '9001'))
args = parser.parse_args()
app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def root(path):
    auth_data = {'client_id': args.client_id,
                'client_secret': args.client_secret,
                'grant_type': 'password',
                'password': args.password,
                'response_type': 'code',
                'username': request.headers['X-User'] if request.headers['X-User'] else args.username
                }
    auth_result = requests.post('{0}{1}'.format(args.endpoint, '/api/v1/users/token'), data=auth_data)

    try:
        access_token = (auth_result.json()['access_token'])
	user_info = requests.get('{0}{1}'.format(args.endpoint, '/api/v1/users/me'), headers={'Authorization': 'Bearer {0}'.format(access_token)}).json()
        refresh_token = (auth_result.json()['refresh_token'])
        token_type = (auth_result.json()['token_type'])
	local_storage_data = ['localStorage.setItem("access_token", "{0}");'.format(access_token),
                              'localStorage.setItem("refresh_token", "{0}");'.format(refresh_token),
                              'localStorage.setItem("token_type", "{0}");'.format(token_type),
                              'localStorage.setItem("id", "{0}");'.format(user_info['id']),
                              'localStorage.setItem("role", "{0}");'.format(user_info['role']),
                              'localStorage.setItem("email", "{0}");'.format(user_info['email']),
                              'localStorage.setItem("username", "{0}");'.format(user_info['username']),
                              'localStorage.setItem("nsfw_policy", "{0}");'.format(user_info['nsfwPolicy']),
                              'localStorage.setItem("auto_play_video", "{0}");'.format(user_info['autoPlayVideo'])]
	local_storage_data = ''.join(local_storage_data)
	response = make_response('<script>{0};window.location.href = "/";</script>'.format(local_storage_data))
	response.set_cookie('peertube_auth', access_token)
        return response
    except Exception as e:
	raise
        return Response(e.args, 401)


if __name__ == '__main__':
     app.run(threaded=True, host=args.host, port=int(args.port))

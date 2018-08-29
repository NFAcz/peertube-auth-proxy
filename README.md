# PeerTube Auth Proxy

## Requirements
 * Python 3
 * python-requests
 * Flask

## Usage
````
$ pip install -r requirements.txt
$ ./app.py 
                              [-s CLIENT_SECRET] [-c CLIENT_ID] [-H HOST]
                              [-P PORT]

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Username
  -p PASSWORD, --password PASSWORD
                        Password
  -s CLIENT_SECRET, --client_secret CLIENT_SECRET
                        Client secret to use
  -c CLIENT_ID, --client_id CLIENT_ID
                        Channel ID to use
  -H HOST, --host HOST  Host name
  -P PORT, --port PORT  Port
````

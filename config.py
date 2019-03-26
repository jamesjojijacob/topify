APP_SESSION_KEY = 'randomkey123'
CLIENT_ID = 'b270d0db21f6420893443e2f2a85e435'
CLIENT_SECRET = '7d2053de49ba4f97a98833412f33f7e7'

# Server-side Parameters
SERVER_IP = '35.242.163.50'
CLIENT_SIDE_URL = 'https://{}'.format(SERVER_IP)
PORT = 8080
REDIRECT_URI_P = '{}/callback/q'.format(CLIENT_SIDE_URL)
REDIRECT_URI = '{}:{}/callback/q'.format(CLIENT_SIDE_URL, PORT)
SCOPE = 'playlist-modify-public playlist-modify-private user-read-email playlist-read-private  user-follow-read user-library-read user-top-read'

#Database parameters

CASSANDRA_HOSTS = 'cassandra'
CASSANDRA_KEYSPACE = 'topify'
APP_SESSION_KEY = 'a-random-key'
CLIENT_ID = 'client-id-from-spotify'
CLIENT_SECRET = 'client-secret-from-spotify'

# Server-side Parameters
SERVER_IP = 'your-server-ip'
CLIENT_SIDE_URL = 'https://{}'.format(SERVER_IP)
PORT = 8080
REDIRECT_URI_P = '{}/callback/q'.format(CLIENT_SIDE_URL)
REDIRECT_URI = '{}:{}/callback/q'.format(CLIENT_SIDE_URL, PORT)
SCOPE = 'playlist-modify-public playlist-modify-private user-read-email playlist-read-private  user-follow-read user-library-read user-top-read'

#Database parameters

CASSANDRA_HOSTS = 'cassandra-hostname'
CASSANDRA_KEYSPACE = 'cassandra-keyspace-name'
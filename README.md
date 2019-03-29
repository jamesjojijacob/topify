# Topify

A web app based on the Spotify [API](<https://developer.spotify.com/documentation/web-api/>).

Topify is a web app that generates personalized recommendations based on a user's most listened to tracks on Spotify. It is built using a Python-Flask backend and leverages the extensive Spotify Web API.

## Demo
<img src="https://media.giphy.com/media/fLpPcc5yDndDFGtJb7/giphy.gif">


## Getting Started

Before testing the code, you have to first obtain a client ID and client secret after registering as a [Spotify Developer](https://developer.spotify.com/dashboard/).

### Setting up Spotify Developer API

Go to the Spotify Dashboard and create a new Client ID. Follow these steps to create your client application.

<img src="https://imgur.com/QJCgwJ1.jpg">

#### Redirect URI

After the app is created, open the app settings and add the callback URI for the host of the app to the Redirect URI whitelist. This is to get the access token to enable authorized requests.

### Environment Setup

Setup a new python virtual environment and install the requirements after cloning the repository.

```python
git clone https://github.com/jamesjojijacob/topify.git
cd topify
python -m venv env
activate
pip install -r requirements.txt
```
#### Database Setup

The database used for the app is Cassandra. To get a local Cassandra instance running, pull the latest Cassandra image from Docker and map the port as follows:

```bash
docker pull cassandra
docker run -d cassandra -p 9042:9042 --name cassandra
docker exec -it cassandra cqlsh
```
To create a keyspace for the app inside the running container:

```CQL
CREATE KEYSPACE topify WITH REPLICATION = {'class' : 'SimpleStrategy', 'replication_factor' : 1};
```
#### Editing config.py

Edit the config.py file to add the Spotify client details, the host IP and the database details.

```python
CLIENT_ID = 'client-id-from-spotify'
CLIENT_SECRET = 'client-secret-from-spotify'
SERVER_IP = 'your-server-ip'
CASSANDRA_HOSTS = 'cassandra-hostname'
CASSANDRA_KEYSPACE = 'cassandra-keyspace-name'
```
To run locally, both CASSANDRA_HOSTS and SERVER_IP should be the localhost IP.

###### Run the app with:

```python
python app.py
```


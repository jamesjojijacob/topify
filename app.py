import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
import random
import requests
import base64
import json
from config import *
from models import *
from flask import Flask, request, render_template, redirect
from flask_cqlalchemy import CQLAlchemy

app = Flask(__name__)
app.config['CASSANDRA_HOSTS'] = [CASSANDRA_HOSTS]
app.config['CASSANDRA_KEYSPACE'] = CASSANDRA_KEYSPACE
app.config['CQLENG_ALLOW_SCHEMA_MANAGEMENT'] = True
db = CQLAlchemy(app)

@app.route('/')
def index():
	
	return render_template('pages/placeholder.index.html')

@app.route('/go')
def go():
	sp_oauth = SpotifyOAuth(CLIENT_ID,CLIENT_SECRET,REDIRECT_URI,scope=SCOPE)
	auth_url = sp_oauth.get_authorize_url()
	return redirect(auth_url)

@app.route('/callback/q')
def callback():
	sp_oauth = SpotifyOAuth(CLIENT_ID,CLIENT_SECRET,REDIRECT_URI,scope=SCOPE)
	access_token = ""
	url = request.url
	code = sp_oauth.parse_response_code(url)	
	token_info = sp_oauth.get_access_token(code)
	access_token = token_info['access_token']
	
	#Creating authorized spotify object
	sp = spotipy.Spotify(access_token)
	
	#Get user data
	user_data = sp.current_user()
	uid = user_data['id']
	email = user_data['email']
	name = user_data['display_name']

	#Add user data to db
	db.sync_db()
	user = Users.create(user_id=uid,user_name=name,user_email=email)

	#Get top tracks
	top_tracks_response=sp.current_user_top_tracks(limit=50)
	top_tracks = []
	for i in range(50):
		top_tracks.append(top_tracks_response['items'][i]['id'])

	#Add tracks to db
	db.sync_db()
	track = Tracks.create(user_id=uid,user_top_tracks=top_tracks)

	#Setting topify user
	top_user = Users.get(user_id=uid).user_id

	#Generating recommendations
	top = []
	top = Tracks.get(user_id=top_user).user_top_tracks
	random.shuffle(top)
	seeds = top[0:5]
	results = sp.recommendations(seed_tracks=seeds,limit=20,country='US')

	#Adding recommended tracks to db
	recommended_tracks = []
	for i in range(20):
		recommended_tracks.append(results['tracks'][i]['id'])
	track.user_recommended_tracks=recommended_tracks
	track.save()

	#Create new playlist
	new_playlist=sp.user_playlist_create(user=top_user, name='Topified Playlist')
	playlist_id=new_playlist['id']
	playlist_url=new_playlist['external_urls']['spotify']

	#Adding playlist data to db
	db.sync_db()
	playlist = Playlists.create(user_id=top_user,user_playlist_id=playlist_id,user_playlist_url=playlist_url)

	#Adding recommended tracks to topify playlist
	
	top_tracks = Tracks.get(user_id=top_user).user_recommended_tracks
	top_playlist = Playlists.get(user_id=top_user).user_playlist_id
	sp.user_playlist_add_tracks(top_user, top_playlist, top_tracks)

	top_name = Users.get(user_id=top_user).user_name
	top_url = Playlists.get(user_id=top_user).user_playlist_url

	return render_template('pages/placeholder.landing.html', name=top_name, pl_url=top_url, user=top_user, playlist=top_playlist)


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=PORT)
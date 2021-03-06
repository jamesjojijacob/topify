import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
import random
import requests
import base64
import json
from config import *
from models import *
from flask import Flask, request, render_template, redirect, session, url_for, jsonify, request
from flask_cqlalchemy import CQLAlchemy

app = Flask(__name__)
app.config['CASSANDRA_HOSTS'] = [CASSANDRA_HOSTS]
app.config['CASSANDRA_KEYSPACE'] = CASSANDRA_KEYSPACE
app.config['CQLENG_ALLOW_SCHEMA_MANAGEMENT'] = True
app.secret_key = APP_SESSION_KEY

db = CQLAlchemy(app)
db.sync_db()
sp_oauth = SpotifyOAuth(CLIENT_ID,CLIENT_SECRET,REDIRECT_URI,scope=SCOPE)

@app.route('/')
def index():
	
	return render_template('pages/placeholder.index.html')

@app.route('/go')
def go():
	
	auth_url = sp_oauth.get_authorize_url()
	return redirect(auth_url)

@app.route('/callback/q')
def callback():
	
	access_token = ""
	url = request.url
	code = sp_oauth.parse_response_code(url)	
	token_info = sp_oauth.get_access_token(code)
	access_token = token_info['access_token']
	session['auth_header'] = {'Authorization': 'Bearer {}'.format(access_token)}

	return redirect(url_for('landing'))
	
@app.route('/landing')
def landing():

	#Creating authorized spotify object
	sp = spotipy.Spotify(auth=session['auth_header'])

	#Get user data
	user_data = sp.current_user()
	uid = user_data['id']
	email = user_data['email']
	name = user_data['display_name']

	#Add user data to db
	Users.create(user_id=uid,user_name=name,user_email=email)

	#Get top tracks
	top_tracks_response=sp.current_user_top_tracks(limit=50)
	returned_count = len(top_tracks_response['items'])

	#handling edge case:0
	new_releases_response=sp.new_releases(country='US', limit=20)
	new_albums=[]
	for i in range(20):
		new_albums.append(new_releases_response['albums']['items'][i]['id'])
	new_albums_response=sp.albums(new_albums)
	new_tracks=[]
	for i in range(20):
		new_tracks.append(new_albums_response['albums'][i]['tracks']['items'][0]['id'])
	
	
	#adding top tracks to db
	if returned_count == 0:
		top_tracks = new_tracks
	else:
		top_tracks = []
		for i in range(returned_count):
			top_tracks.append(top_tracks_response['items'][i]['id'])
	
	#Generating recommendations
	shuffled = top_tracks 
	random.shuffle(shuffled)
	seeds = shuffled[0:5]
	results = sp.recommendations(seed_tracks=seeds,limit=20,country='US')

	#Extracting tracks to display
	recommended_tracks = []
	for i in range(20):	
		recommended_tracks.append(results['tracks'][i]['id'])

	Tracks.create(user_id=uid,user_top_tracks=top_tracks,user_recommended_tracks=recommended_tracks)

	playlist_name = 'Topified Playlist'
		
	#Check if Topify playlist already exists for user
	user_existing_playlists_response=sp.user_playlists(uid, limit=50)
	user_existing_playlists_count = len(user_existing_playlists_response['items'])
	user_existing_playlists=[]
	for i in range(user_existing_playlists_count):
		user_existing_playlists.append(user_existing_playlists_response['items'][i]['name'])
		if playlist_name in user_existing_playlists:
			for item in user_existing_playlists_response['items']:
				if item.get('name') == playlist_name :
					#Get exisiting playlist
					playlist_id = item.get('id')
					playlist_url = item.get('external_urls')['spotify']
		else:
			#Create new playlist
			new_playlist=sp.user_playlist_create(user=uid, name=playlist_name)
			playlist_id=new_playlist['id']
			playlist_url=new_playlist['external_urls']['spotify']

	#Adding playlist data to db
	Playlists.create(user_id=uid,topify_playlist_id=playlist_id,topify_playlist_url=playlist_url,topify_playlist_name=playlist_name)

	#Setting current user
	top_user = Users.get(user_id=uid).user_id
	top_name = Users.get(user_id=uid).user_name
	top_url = Playlists.get(user_id=uid).topify_playlist_url
	top_tracks = Tracks.get(user_id=uid).user_recommended_tracks
	top_playlist = Playlists.get(user_id=uid).topify_playlist_id

	#Adding recommended tracks to topify playlist

	sp.user_playlist_replace_tracks(top_user, top_playlist, top_tracks)

	return render_template('pages/placeholder.landing.html', name=top_name, pl_url=top_url, user=top_user, playlist=top_playlist)

@app.route('/recommend')
def recommend():
	#Creating authorized spotify object
	sp = spotipy.Spotify(auth=session['auth_header'])

	user_data = sp.current_user()
	uid = user_data['id']

	#Regenerating recommendations
	top = []
	top = Tracks.get(user_id=uid).user_top_tracks
	random.shuffle(top)
	seeds = top[0:5]
	results = sp.recommendations(seed_tracks=seeds,limit=20,country='US')
	recommended_tracks = []
	for i in range(20):
		recommended_tracks.append(results['tracks'][i]['id'])
	
	#Replacing recommended tracks in database

	Tracks(user_id=uid).update(user_recommended_tracks=recommended_tracks)

	#Replacing recommended tracks in topify playlist

	top_user = Users.get(user_id=uid).user_id
	top_tracks = Tracks.get(user_id=uid).user_recommended_tracks
	top_playlist = Playlists.get(user_id=uid).topify_playlist_id
	sp.user_playlist_replace_tracks(top_user, top_playlist, top_tracks)

	#Setting current user
	
	top_name = Users.get(user_id=uid).user_name
	top_url = Playlists.get(user_id=uid).topify_playlist_url

	return render_template('pages/placeholder.landing.html', name=top_name, pl_url=top_url, user=top_user, playlist=top_playlist)

@app.route('/playlist',methods=['POST'])
def add_playlist():

	if not request.form['playlist_name']:
		return jsonify({'error':'the new playlist needs to have a name'}), 400
	
	playlist_name = request.form['playlist_name']

	#Creating authorized spotify object
	sp = spotipy.Spotify(auth=session['auth_header'])

	#Getting current user
	user_data = sp.current_user()
	uid = user_data['id']

	new_playlist=sp.user_playlist_create(user=uid, name=playlist_name)
	playlist_id=new_playlist['id']
	playlist_url=new_playlist['external_urls']['spotify']
	#Adding playlist data to db
	Created.create(user_id=uid,user_playlist_id=playlist_id,user_playlist_url=playlist_url,user_playlist_name=playlist_name)

	top_user = Users.get(user_id=uid).user_id
	top_tracks = Tracks.get(user_id=uid).user_recommended_tracks
	top_playlist = Created.get(user_id=uid).user_playlist_id
	sp.user_playlist_add_tracks(top_user, playlist_id, top_tracks)

	return jsonify({'message': 'created: {}'.format(playlist_name)}), 201
if __name__ == '__main__':
	app.run('0.0.0.0', port=PORT, ssl_context=('device.crt', 'device.key'))
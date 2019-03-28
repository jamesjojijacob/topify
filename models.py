from flask_cqlalchemy import CQLAlchemy
from app import db

# Set classes here

class Users(db.Model):
    user_id = db.columns.Text(primary_key=True,required=True)
    user_name = db.columns.Text(required=True)
    user_email = db.columns.Text(required=False)
    
class Tracks(db.Model):
    user_id = db.columns.Text(primary_key=True,required=True)
    user_top_tracks = db.columns.List(db.columns.Text,required=True)
    user_recommended_tracks = db.columns.List(db.columns.Text,required=True)

class Playlists(db.Model):
    user_id = db.columns.Text(primary_key=True,required=True)
    topify_playlist_id = db.columns.Text(required=False)
    topify_playlist_url = db.columns.Text(required=False)
    topify_playlist_name = db.columns.Text(required=True)
    
class Created(db.Model):
    user_id = db.columns.Text(primary_key=True,required=True)
    user_playlist_id = db.columns.Text(required=False)
    user_playlist_url = db.columns.Text(required=False)
    user_playlist_name = db.columns.Text(required=True)
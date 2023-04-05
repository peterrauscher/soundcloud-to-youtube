import os

from ytmusicapi import YTMusic

ytmusic = YTMusic(auth="headers_auth.json")
response = ytmusic.get_library_upload_songs(limit=None)
for song in response:
    ytmusic.delete_upload_entity(song["entityId"])

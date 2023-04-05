import json
import os
import time

from ytmusicapi import YTMusic

ytmusic = YTMusic(auth="headers_auth.json")


try:
    with open("playlists.json") as fp:
        playlist_database = json.load(fp)

    for playlist in playlist_database:
        uploaded_titles = []
        directory_path = os.path.join("output", playlist["path"])
        for filename in os.listdir(directory_path):
            if filename.endswith(".info.json"):
                with open(os.path.join(directory_path, filename), "r") as f:
                    metadata = json.load(f)
                    song_id = metadata["id"]
                    # skip songs already in the playlist
                    if song_id in playlist["added_songs"]:
                        continue
                    print("Uploading: %s" % metadata["title"])
                    song_path = os.path.join(directory_path, song_id + ".mp3")
                    result = ytmusic.upload_song(filepath=song_path)
                    uploaded_titles.append(metadata["title"])
                    playlist["added_songs"].append(song_id)
        uploaded_songs = ytmusic.get_library_upload_songs(
            limit=len(uploaded_titles), order="recently_added"
        )
        add_to_playlist = []
        for uploaded_song in uploaded_songs:
            add_to_playlist.append(uploaded_song["videoId"])
        # Create or edit playlist
        if playlist["yt_music_id"] != "":
            ytmusic.get_playlist(playlist["yt_music_id"], limit=None)
            ytmusic.add_playlist_items(
                playlist["yt_music_id"], videoIds=add_to_playlist
            )
        else:
            playlist["yt_music_id"] = ytmusic.create_playlist(
                playlist["name"], playlist["description"], video_ids=add_to_playlist
            )
        print("All done! Checkout your results at https://music.youtube.com")
except:
    print("Failed to upload all songs!")
    with open("playlists.json") as fp:
        fp.write(json.dumps(playlist_database))

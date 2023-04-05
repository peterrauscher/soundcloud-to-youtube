import json
import os
import shlex
import subprocess
from io import StringIO

from slugify import slugify

# Load the playlists from the JSON file
with open("playlists.json") as f:
    playlists = json.load(f)


def download_playlists():
    # Loop through each playlist URL and run the command
    for playlist in playlists:
        playlist["path"] = slugify(playlist["name"])
        command = f'yt-dlp --downloader aria2c --no-write-playlist-metafiles --write-info-json --write-thumbnail -P "home:output/{playlist["path"]}" -o "%(id)s.mp3" {playlist["soundcloud_link"]}'
        with subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True,
            shell=True,
        ) as p, StringIO() as buf:
            for line in p.stdout:
                print(line, end="")
                buf.write(line)
            output = buf.getvalue()
        print("ty-dlp command returned with status code".format(str(p.returncode)))


def tag_files():
    for playlist in playlists:
        directory_path = os.path.join("output", playlist["path"])
        # Rename all weirdly named thumbnails
        for filename in os.listdir(directory_path):
            if filename.endswith(".mp3.jpg"):
                try:
                    os.rename(
                        os.path.join(directory_path, filename),
                        os.path.join(
                            directory_path, filename.replace(".mp3.jpg", ".jpg")
                        ),
                    )
                except OSError as e:
                    print(
                        "Failed to rename thumbnail with .mp3.jpg extension: %s - %s."
                    ) % (
                        e.filename,
                        e.strerror,
                    )
        # Now do the tagging
        for filename in os.listdir(directory_path):
            if filename.endswith(".info.json"):
                try:
                    with open(os.path.join(directory_path, filename), "r") as f:
                        metadata = json.load(f)
                        song_id = metadata["id"]
                        thumbnail_path = os.path.join(directory_path, song_id + ".jpg")
                        song_path = os.path.join(directory_path, song_id + ".mp3")
                        tagged_song_path = os.path.join(
                            directory_path, song_id + "-tagged.mp3"
                        )
                        if not (
                            os.path.exists(song_path) and os.path.exists(thumbnail_path)
                        ):
                            continue
                        song_title = shlex.quote(
                            metadata["title"].replace("'", "").replace('"', "")
                        )
                        song_artist = shlex.quote(
                            metadata["uploader"].replace("'", "").replace('"', "")
                        )
                        command = f'lame --ti "{thumbnail_path}" --tt {song_title} --ta {song_artist} --tl "{playlist["path"]}" "{song_path}" "{tagged_song_path}"'
                        with subprocess.Popen(
                            command,
                            stdout=subprocess.PIPE,
                            bufsize=1,
                            universal_newlines=True,
                            shell=True,
                        ) as p, StringIO() as buf:
                            for line in p.stdout:
                                print(line, end="")
                                buf.write(line)
                            output = buf.getvalue()
                        print(
                            "lame command returned with status code {}".format(
                                str(p.returncode)
                            )
                        )
                        try:
                            os.remove(song_path)
                            os.remove(thumbnail_path)
                        except OSError as e:
                            print(
                                "Failed deleting untagged song: %s - %s."
                                % (e.filename, e.strerror)
                            )
                        try:
                            os.rename(tagged_song_path, song_path)
                        except OSError as e:
                            print("Failed to rename tagged song: %s - %s.") % (
                                e.filename,
                                e.strerror,
                            )
                except Exception as e:
                    print(e)


if __name__ == "__main__":
    download_playlists()
    tag_files()
    with open("playlists.json", "w") as f:
        f.write(json.dumps(playlists))
        f.close()

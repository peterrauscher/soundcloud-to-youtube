const { spawn } = require("child_process");
const fs = require("fs");
const sanitize = require("sanitize-filename");
const playlists = require("./playlists.json");

function downloadSoundCloudPlaylists() {
  // Loop through each playlist URL and run the command
  for (const playlist of playlists) {
    let playlist_folder = sanitize(playlist.name);
    let command = `yt-dlp --downloader aria2c --write-info-json --write-playlist-metafiles --write-thumbnail -P "home:output/${playlist_folder}" ${playlist.soundcloud_link}`;
    const child = spawn(command, { shell: true });

    // Log any output from the command to the console
    child.stdout.on("data", (data) => {
      console.log(`stdout:\n${data}`);
    });

    child.stderr.on("data", (data) => {
      console.error(`stderr:\n${data}`);
    });

    // Log any errors that occur when executing the command
    child.on("error", (error) => {
      console.error(`Failed to execute command: ${error}`);
    });

    // Log the exit status of the command
    child.on("close", (code) => {
      console.log(`Command exited with code ${code}`);
    });
  }
}

(() => {
  // Pulling ourselves up by our bootstraps
  downloadSoundCloudPlaylists();
})();

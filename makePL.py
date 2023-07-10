import json
from cred import user_id
from cred import spotify_token
import requests
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
import youtube_dl
global nationCode
nationCode = input("Enter the 2 letter nation code you would like to select (ISO 3166-1 alpha-2 naming) [ex: United States = US, Canada = CA]:")
class makePL:
    # Initialization function which sets up necessary user and API details
    def __init__(self):
        self.user = user_id  # Spotify user id
        self.spotify_token = spotify_token  # Spotify token for authenticated requests
        self.youtube = self.loginYT()  # Authenticated YouTube client
        self.song_info = {}  # Data structure to store song information

    # Function that performs the login to the YouTube API using OAuth
    def loginYT(self):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"
        # Google's OAuth flow with installed app option
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()  # Obtain valid credentials
        # Build the YouTube client
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)
        return youtube

    # Function to get YouTube videos in a playlist and extract relevant song info
    def getYTPlaylist(self):
        request = self.youtube.videos().list(
        part="snippet,contentDetails,statistics",
        chart="mostPopular",
        regionCode=nationCode
        )
        response = request.execute()

        # For each video in the response, fetch the song details
        for item in response["items"]:
            vid_name = item["snippet"]["title"]
            yturl = "https://www.youtube.com/watch?v={}".format(item["id"])
            video = youtube_dl.YoutubeDL({}).extract_info(yturl, download=False)
            song_name = video.get("track")
            artist = video.get("artist")

            # If song name and artist are found, store them in the song_info dictionary
            if song_name and artist:
                self.song_info[vid_name] = {
                        "yturl": yturl,
                        "song_name": song_name,
                        "artist": artist,
                        "spURI": self.searchSP(song_name, artist)  # search in Spotify
                }

    # Function to make a new playlist in Spotify
    def makePL(self):
        # Prepare the playlist's details
        request_body = json.dumps({
            "name" : "Most Popular Video Soundtrack in "+ nationCode,
            "description" : "Auto-generated list of songs based on the most popular videos in the selected country",
            "public" : "false"
        })

        # Make the playlist using the Spotify API
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user)
        response = requests.post(
            query,
            data = request_body,
            headers ={
                "Content-Type":"application/json",
                "Authorization":"Bearer {}".format(spotify_token)
            },
        )
        response_json = response.json()
        return response_json["id"]

    # Function to search for a song in Spotify
    def searchSP(self, song_name, artist):
        # Formulate the search query
        query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track".format(
            song_name,
            artist
        )

        # Perform the search
        response = requests.get(
            query,
            headers ={
                "Content-Type":"application/json",
                "Authorization":"Bearer {}".format(self.spotify_token)
            },
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]
        return songs[0]["uri"]

    # Function to add songs to the newly created Spotify playlist
    def addSong(self):
        # Get the YouTube playlist's info
        self.getYTPlaylist()

        # Prepare the list of song URIs
        songURI =[]
        for i, info in self.song_info.items():
            songURI.append(info["spURI"])

        # Create a new playlist
        newPlay = self.makePL()

        # Prepare the request to add songs
        request_data = json.dumps(songURI)
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(newPlay)

        # Add songs to the playlist
        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.spotify_token)
            }
        )
        return "Playlist Created"

if __name__ == '__main__':
    cp = makePL()  # Instantiate the makePL class
    cp.addSong()  # Call the addSong function to create the playlist

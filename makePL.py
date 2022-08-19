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
    def __init__(self):
        self.user = user_id
        self.spotify_token = spotify_token
        self.youtube = self.loginYT()
        self.song_info = {}
        

        #client fetcher

    def loginYT(self):
        # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"

        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            chart="mostPopular",
            regionCode=nationCode
        )
        response = request.execute()
        print(response)
    def getYTPlaylist(self):
        #from YouTube API: gathers popular videos in specified country
        
        request = self.youtube.videos().list(
        part="snippet,contentDetails,statistics",
        chart="mostPopular",
        regionCode=nationCode
    )
        response = request.execute()
        #loop through videos & use YouTubeDL Library to extract song identifications
        for item in response["items"]:
            vid_name = item["snippet"]["title"]
            yturl = "https://www.youtube.com/watch?v={}".format(item["id"])

            video = youtube_dl.YoutubeDL({}).extract_info(yturl, download=False)
            song_name = video["track"]
            artist = video["artist"]
            self.songdata[vid_name] = {
                    "yturl": yturl,
                    "song_name": song_name,
                    "artist": artist,
                    "spURI": self.searchSP(song_name, artist)
            }
            #plug data into spotify's search API
        

    #makePL creates the playlist entry
    def makePL(self):
        request_body = json.dumps({
            "name" : "Most Popular Video Soundtrack in "+ nationCode,
            "description" : "Auto-generated list of songs based on the most popular videos in the selected country",
            "public" : "false", #I'd like everyone to know I'm really big on privacy
        })
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

    #searchSP finds the song in spotify's library
    def searchSP(self, song_name, artist):
        query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track".format(
            song_name,
            artist
        ) #passing in song info to derive URL

        response = requests.get(
            query,
            headers ={
                "Content-Type":"application/json",
                "Authorization":"Bearer {}".format(self.spotify_token)
            },
        )

        response_json = response.json()
        songs = response_json["tracks", "items"]
        return songs[0]["uri"]


        
    def addSong(self):
        self.getYTPlaylist()
        #take in Song URI's
        songURI =[]
        for i, info in self.song_info.items():
            songURI.append(info["spURI"])
        #make & add playlist contents
        newPlay = self.makePL()
        request_data = json.dumps(songURI)
        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(newPlay)
        
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
    cp = makePL()
    cp.addSong()
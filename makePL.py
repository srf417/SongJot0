import json
from cred import user_id
import requests
class makePL:
    def __init__(self):
        self.user = user_id
    def loginYT(self):
        pass
    def getLiked(self):
        pass
    def makePL(self):
        request_body = json.dumps({
            "name" : "Liked YouTube Video Soundtrack",
            "description" : "Auto-generated list of songs found in your liked YouTube videos",
            "public" : "false",
        })

        response = requests.post(
            query = "https://api.spotify.com/v1/users/{}/playlists".format(self.user),
            data = request_body
            headers ={
                "Content-Type":"application/json",
                "Authorization":"Bearer {}".format(spotify_token)
            }
            response_json = response.json()
            return response_json["PL_id"]
        )
    def searchSP(self):
        pass
    def addSong(self):
        pass
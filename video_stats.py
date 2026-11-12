import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError("No se encontró YOUTUBE_API_KEY en el archivo .env")

CHANNEL_HANDLE = os.getenv("CHANNEL_HANDLE")

if not CHANNEL_HANDLE:
    raise ValueError("No se encontró CHANNEL_HANDLE en el archivo .env")

maxResults = 50

def get_playlist_id():
    try: 

        url = "https://youtube.googleapis.com/youtube/v3/channels"

        params = {
            "part": "contentDetails",
            "forHandle": CHANNEL_HANDLE,
            "key": API_KEY
        }

        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        #print(json.dumps(data, indent=4))

        channel_items = data['items'][0]

        channel_playlistId = channel_items['contentDetails']['relatedPlaylists']['uploads']

        #print(channel_playlistId)

        return channel_playlistId

    except requests.exceptions.RequestException as e:
        raise e

def get_video_ids(playlistId): 

    video_ids = []

    pageToken = None

    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistId}&key={API_KEY}"

    try:
        while True:

            url = base_url

            params = {
                "part": "contentDetails",
                "playlistId": playlistId,
                "maxResults": 50,
                "key": API_KEY
            }

            if pageToken:
                params["pageToken"] = pageToken

            response = requests.get(url, params=params, timeout=15)

            response.raise_for_status()

            data = response.json()

            for item in data.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)

            pageToken = data.get('nextPageToken')

            if not pageToken:
                break

        return video_ids
    
    except requests.exceptions.RequestException as e:
        raise e

def batch_list(video_id_list, batch_size):
    for i in range(0, len(video_id_list), batch_size):
        yield video_id_list[i:i + batch_size]



def extract_video_data(video_ids):

    extracted_data = []

    url = "https://www.googleapis.com/youtube/v3/videos"
    try: 

        for batch in batch_list(video_ids, maxResults):

            video_ids_str = ",".join(batch)

            params = {
                "part": "snippet,contentDetails,statistics",
                "id": video_ids_str,
                "key": API_KEY
            }

            response = requests.get(
                url,
                params=params,
                timeout=15
            )

            if not response.ok:
                raise RuntimeError(
                    f"Error HTTP {response.status_code} al consultar videos"
                )

            data = response.json()

            for item in data.get("items", []):

                video_id = item["id"]
                snippet = item["snippet"]
                contentDetails = item["contentDetails"]
                statistics = item["statistics"]

                video_data = {
                    "video_id": video_id,
                    "title": snippet.get("title"),
                    "publishedAt": snippet.get("publishedAt"),
                    "duration": contentDetails.get("duration"),
                    "viewCount": statistics.get("viewCount"),
                    "likeCount": statistics.get("likeCount"),
                    "commentCount": statistics.get("commentCount")
                }

                extracted_data.append(video_data)

            return extracted_data


    except requests.exceptions.RequestException as e:
        raise e 


    
if __name__ == "__main__":
    playlist_id = get_playlist_id()
    video_ids = get_video_ids(playlist_id)
    extract_video_data(video_ids)




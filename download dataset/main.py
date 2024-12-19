import requests
import json

API_KEY = 'bec4faac254bf82a27de975b6eaccf1d'
URL = "http://ws.audioscrobbler.com/2.0/"
TRACKS_LIMIT = 2000  # Tổng số bài hát
PAGE_SIZE = 50       # Số bài mỗi lần gọi
total_pages = TRACKS_LIMIT // PAGE_SIZE

all_tracks = set()  # Dùng set để loại bỏ trùng lặp

def fetch_top_tracks(page):
    params = {
        'method': 'chart.getTopTracks',
        'api_key': API_KEY,
        'format': 'json',
        'limit': PAGE_SIZE,
        'page': page
    }
    response = requests.get(URL, params=params)
    if response.status_code == 200:
        data = response.json()
        tracks = data['tracks']['track']
        return {(track['name'], track['artist']['name']) for track in tracks}  # Dùng tuple
    else:
        print(f"Error {response.status_code}")
        return set()

# Gọi API và lưu kết quả
for page in range(1, total_pages + 1):
    print(f"Fetching page {page}...")
    tracks = fetch_top_tracks(page)
    all_tracks.update(tracks)  # Thêm vào set để loại bỏ trùng lặp

# Lưu kết quả vào file
unique_tracks = list(all_tracks)
with open('unique_top_tracks.json', 'w', encoding='utf-8') as f:
    json.dump(unique_tracks, f, ensure_ascii=False, indent=4)

print(f"Fetch complete! Collected {len(unique_tracks)} unique tracks. Data saved to 'unique_top_tracks.json'")


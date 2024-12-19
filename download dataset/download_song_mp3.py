import os
import json
from yt_dlp import YoutubeDL

def download_audio_from_youtube(query, output_path):
    """Download audio from YouTube based on a search query."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query} lyrics", download=True)['entries'][0]
            return info['title'] + ".mp3"
        except Exception as e:
            print(f"Failed to download {query}: {e}")
            return None

def organize_audio_files(audio_path):
    # Đọc file JSON hiện tại   
    input_file = 'unique_top_tracks.json'
    output_file = 'converted_tracks.json'

    # Mở file JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        tracks = json.load(f)

    if not os.path.exists(audio_path):
        os.makedirs(audio_path)

    converted_tracks = []
    for idx, (title, artist) in enumerate(tracks, start=1):
        track_data = {
            "id": idx,
            "filename": f"{title}.mp3",
            "title": title,
            "artist": artist
        }
        
        target_file_path = os.path.join(audio_path, f"{title}.mp3")

        # Check if the file already exists
        if os.path.exists(target_file_path):
            print(f"File already exists: {target_file_path}, skipping download.")
            continue

        print(f"Processing: {title}")
        # Download the song as mp3
        downloaded_file = download_audio_from_youtube(title + artist + "lyrics", audio_path)

        if downloaded_file:
            invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']  
            for char in invalid_chars:  
                downloaded_file = downloaded_file.replace(char, '')
            old_path = os.path.join(audio_path, downloaded_file)
            new_path = os.path.join(audio_path, f"{title}.mp3")

            # Rename the file to match the folder name
            os.rename(old_path, new_path)
            print(f"Downloaded and renamed: {title} -> {new_path}")
        else:
            print(f"Failed to process: {title}")
        
        converted_tracks.append(track_data)
    
    # Ghi kết quả vào file mới
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted_tracks, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    base_path = os.getcwd()  
    audio_dir = os.path.join(base_path, "audio")

    organize_audio_files(audio_dir)

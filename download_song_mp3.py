import os
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

def organize_audio_files(humming_path, audio_path):
    """Organize audio files into the audio directory with proper naming."""
    if not os.path.exists(audio_path):
        os.makedirs(audio_path)

    for song_folder in os.listdir(humming_path):
        song_path = os.path.join(humming_path, song_folder)
        if os.path.isdir(song_path):

            target_file_path = os.path.join(audio_path, f"{song_folder}.mp3")

            # Check if the file already exists
            if os.path.exists(target_file_path):
                print(f"File already exists: {target_file_path}, skipping download.")
                continue

            print(f"Processing: {song_folder}")
            # Download the song as mp3
            downloaded_file = download_audio_from_youtube(song_folder, audio_path)

            if downloaded_file:
                old_path = os.path.join(audio_path, downloaded_file)
                new_path = os.path.join(audio_path, f"{song_folder}.mp3")

                # Rename the file to match the folder name
                os.rename(old_path, new_path)
                print(f"Downloaded and renamed: {song_folder} -> {new_path}")
            else:
                print(f"Failed to process: {song_folder}")

if __name__ == "__main__":
    base_path = os.getcwd()  # Adjust this if you need a specific base directory
    humming_dir = os.path.join(base_path, "Humming Audio")
    audio_dir = os.path.join(base_path, "audio")

    organize_audio_files(humming_dir, audio_dir)

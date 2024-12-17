import os
from search_1 import search_1
from search_2 import search_2
from search_3 import search_3
import json
import shutil

def setup_search_directories():
    directories = ['search', 'search/processed', 'search/embedding', 'search/results']
    for dir in directories:
        os.makedirs(dir, exist_ok=True)

def cleanup_search_directories():
    if os.path.exists('search'):
        shutil.rmtree('search')

def copy_input_file(input_file):
    os.makedirs('search', exist_ok=True)
    output_path = os.path.join('search', os.path.basename(input_file))
    shutil.copy2(input_file, output_path)
    return output_path

def run_search_pipeline(input_file):
    try:
        cleanup_search_directories()
        setup_search_directories()

        copy_input_file(input_file)

        search_1('search', 'search')
        search_2('search', 'search', 'checkpoints/resnetface_best.pth')
        results = search_3('search', 'search')

        results_file = os.path.join('search', 'results', 'search_results.json')
        if os.path.exists(results_file):
            with open(results_file, 'r') as f:
                search_results = json.load(f)

            # Format results for UI
            formatted_results = []
            seen_songs = set()

            for query_name, query_results in search_results.items():
                for match in query_results['matches']:
                    song_info = match['info']

                    if song_info in seen_songs:
                        continue

                    seen_songs.add(song_info)

                    if " - " in song_info:
                        artist, title = song_info.split(" - ", 1)
                    else:
                        artist = "Unknown Artist"
                        title = song_info

                    max_distance = 1000.0
                    confidence = max(0, min(100, (1 - match['distance'] / max_distance) * 100))

                    formatted_results.append({
                        "title": title,
                        "artist": artist,
                        "match": f"{confidence:.1f}%"
                    })

            formatted_results.sort(key=lambda x: float(x['match'].strip('%')), reverse=True)

            return formatted_results[:20]

    except Exception as e:
        raise Exception(f"Search pipeline error: {str(e)}")

    return []

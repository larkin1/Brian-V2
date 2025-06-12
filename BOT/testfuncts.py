# Testing ground for new features and functions.
import time

def test(data, client):
    time.sleep(2)
    client.sendText('REDACTED@c.us', "eeee")
    time.sleep(10)

# from ytmusicapi import YTMusic
# import concurrent.futures

# music = YTMusic('BOT/YT/YtMusicAuth.json')

# def songLookup(songs: list) -> tuple:
#     """Uses the YT music search api to lookup songs and return a list. the first result in the tuple is the songs, and the second is the errors."""
    
#     results = []
#     errors = []
    
#     def safe_search(item):
#         try:
#             return music.search(item, filter='songs')
#         except Exception as e:
#             errors.append((item, str(e)))
#             return None
    
#     with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        
#         results = list(executor.map(safe_search, songs))
    
#     return (results, errors)
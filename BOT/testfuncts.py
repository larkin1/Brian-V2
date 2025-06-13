# Testing ground for new features and functions.
import time

async def test(data, client):
    try:
        message = await client.sendText(data.get("chatId"), "test meddahe")
        print(message.get("id"))
        for i in range(10):
            time.sleep(0.2)
            await client.editMessage(message.get("id").removesuffix("_out"), f"Test Number: {str(i)}")
    except Exception as e: print(e)

from ytmusicapi import YTMusic
import concurrent.futures

music = YTMusic('BOT/YT/YtMusicAuth.json')

def songLookup(songs: list) -> tuple:
    """Uses the YT music search api to lookup songs and return a list. the first result in the tuple is the songs, and the second is the errors."""
    
    results = []
    errors = []
    
    def safe_search(item):
        try:
            return music.search(item, filter='songs')
        except Exception as e:
            errors.append((item, str(e)))
            return None
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        
        results = list(executor.map(safe_search, songs))
    
    return (results, errors)
from ytmusicapi import YTMusic
from yt_dlp import YoutubeDL
from PIL import Image
import os, zipfile, BOT.utils as utils, concurrent.futures, subprocess, uuid, re

bannedchars = "<>:\"/\\|?*"
def zipFolder(path, maxSize=None, savePath="", name="Zipped"):
    
    if savePath and not os.path.exists(savePath):
        os.makedirs(savePath)
    
    if type(path) == str:
        filesInDir = [os.path.join(path, f) for f in os.listdir(path)]
    else:
        filesInDir = path
    currentSize = 0
    zipnum = 1
    fileListList = []
    fileList = []

    for file in filesInDir:
        size = os.path.getsize(file)
        if maxSize and (currentSize + size > maxSize) and fileList:
            fileListList.append(fileList)
            fileList = []
            currentSize = 0
        fileList.append(file)
        currentSize += size
    if fileList:
        fileListList.append(fileList)

    paths = []
    for idx, fileList in enumerate(fileListList):
        zip_path = os.path.join(savePath, f"{name}{idx+1}.zip")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for j in fileList:
                if os.path.isfile(j):
                    arcname = os.path.basename(j)
                    zipf.write(j, arcname)
                    # os.remove(j)  # Uncomment if you want to delete files after zipping
                else:
                    print(f"[Error] Path: {j} does not exist. Skipping...")
        paths.append(zip_path)
    return paths

music = YTMusic('BOT/YT/YtMusicAuth.json')

def songLookup(songs: list) -> tuple:
    """Uses the YT music search api to lookup songs and return a list. the first result in the tuple is the songs, and the second is the errors."""
    results = []
    errors = []
    
    def search(item):
        try:
            return music.search(item, filter='songs', limit=1)
        except Exception as e:
            errors.append((item, str(e)))
            return None
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(search, songs))
        
    cookedResults = []
    for i in results:
        item = i[0]
        artists = item.get("artists", [])
        arts = ", ".join(j.get("name", "") for j in artists)
        cookedResults.append(
            {"title":item.get("title", ""), 
             "id":item.get("videoId", ""), 
             "artists":arts}
        )
        
    return (cookedResults, errors)

def albumLookup(album: str) -> tuple:
    """Uses the YT music search api to lookup songs and return a list. the first result in the tuple is the songs, and the second is the errors."""
    results = []
    errors = []
    def search(item):
        try:
            return music.search(item, filter='albums', limit=1)
        except Exception as e:
            errors.append((item, str(e)))
            return None
    result = search(album)
    item = result[0]
    id = item["playlistId"]
    link = f"https://music.youtube.com/playlist?list={id}"
    title = item['title']
    artist = item['artists'][0]['name']
    
    with YTMusic() as lookup:
        id = lookup.get_album_browse_id(id)
        file = lookup.get_album(id)
        
    results = file.get("tracks")    
    listOfSongs = []
    for i in results:
        artist = ''
        for j in i['artists']:
            artist += j['name']+', '
        artist = artist.strip(", ")
        titlee = i["title"]
        listOfSongs.append((artist, titlee))

    searchTerms = [f'"{i[1]}" "{title}" "{i[0]}"' for i in listOfSongs]
    
    listOfSongs = songLookup(searchTerms)[0]
    
    songs = []
    for i in listOfSongs:
        songs.append({
            "title": i.get("title", ""),
            "id": i.get("id", ""),
            "artists": i.get("artists", ""),
            "songNumber": listOfSongs.index(i) + 1,
        })
                
    return (songs, title, artist, errors)

def downloadSongs(songList: list, outputDir: str="TEMP/YTMusicDownloads", maxWorkers: int=4):
    os.makedirs(outputDir, exist_ok=True)
    
    def download(song):
        url = f"https://music.youtube.com/watch?v={song['id']}"
        def safe_filename(s, maxlen=80):
            s = re.sub(r'[<>:"/\\|?*\']', '', s)  # remove bad chars
            return s[:maxlen]

        title = safe_filename(song['title'], 100)
        artists = safe_filename(song['artists'], 40)
        filename = f"{title} - {artists}.%(ext)s"
        filepath = os.path.join(outputDir, filename)

        if any(os.path.exists(filepath.replace('%(ext)s', ext)) for ext in ['mp3', 'm4a', 'webm']):
            return filepath.replace('%(ext)s', "mp3")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': filepath,
            'writethumbnail': True,
            "cookiefile": "BOT/YT/ytdlp-cookies.txt",
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
                {
                    'key': 'FFmpegMetadata',
                },
            ],
            'quiet': True,
            'no_warnings': True,
            'noprogress': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
            basepath = filepath.rsplit(".", 1)[0]
            thumbnail_path = basepath + ".webp"
            audio_path = basepath + ".mp3"

            # Square the thumbnail
            if os.path.exists(thumbnail_path):
                try:
                    img = Image.open(thumbnail_path).convert("RGB")
                    width, height = img.size
                    side = min(width, height)
                    left = (width - side) // 2
                    top = (height - side) // 2
                    img_cropped = img.crop((left, top, left + side, top + side))
                    jpg_path = thumbnail_path.rsplit(".", 1)[0] + ".jpg"
                    img_cropped.save(jpg_path, format='WEBP')
                except Exception as e:
                    print(f"{utils.Colors.White}{utils.Colors.Red}[YT.Downloads] [Error] {utils.Colors.White}DownloadError: {utils.Colors.Blue}Error cropping thumbnail: {e}{utils.Colors.White}")

                # Embed cropped thumbnail using ffmpeg
                try:
                    subprocess.run([
                        'ffmpeg', '-y',
                        '-i', audio_path,
                        '-i', jpg_path,
                        '-map', '0:a', '-map', '1:v',
                        '-c:a', 'copy',
                        '-c:v', 'mjpeg',
                        '-id3v2_version', '3',
                        '-metadata:s:v', 'title=Album cover',
                        '-metadata:s:v', 'comment=Cover (front)',
                        audio_path + ".temp.mp3"
                    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    os.replace(audio_path + ".temp.mp3", audio_path)
                    os.remove(thumbnail_path)
                    os.remove(jpg_path)
                except Exception as e:
                    print(f"{utils.Colors.White}{utils.Colors.Red}[YT.Downloads] [Error] {utils.Colors.White}DownloadError: {utils.Colors.Blue}Error embedding thumbnail: {e}{utils.Colors.White}")
                            
        return audio_path

    with concurrent.futures.ThreadPoolExecutor(max_workers=maxWorkers) as executor:
        results = list(executor.map(download, songList))

    return results

def multiSongDl(songs: list):
    """Downloads Songs from search terms to a dir, and returns the dir.

    Args:
        songs (list): A list of Search terms as strings.
    """
    def dedup_dicts(seq, key):
        seen = set()
        out = []
        for d in seq:
            k = d[key]
            if k not in seen:
                seen.add(k)
                out.append(d)
        return out
    
    requestId = uuid.uuid4()
    results = songLookup(songs)
    
    data = [{"title":i.get("title"), "artist":i.get("artists")} for i in results[0]]
    yield data
    yield results[1]
    
    songs = dedup_dicts(results[0], "id")
    
    try:
        paths = downloadSongs(songs)
        zip = zipFolder(paths, 10**8, "TEMP/YTMusicZips", str(requestId))
        for i in paths:
            os.remove(i)
    except Exception as error:
        print(f"{utils.Colors.White}{utils.Colors.Red}[YT.Downloads] [Error] {utils.Colors.White}DownloadError: {utils.Colors.Blue}Error Downloading/Zipping Songs: {error}{utils.Colors.White}")
    
    yield zip

def singleSongDl(song: str):
    """Downloads a Song from a search term to a dir, and returns the path.
    
    Args:
        song (str): A Search term as a string."""

    results = songLookup([song])
    
    data = {"title":results[0][0].get("title"), "artist":results[0][0].get("artists")}
    
    yield data
        
    yield results[1]
    
    try:
        path = downloadSongs([results[0][0]])[0]
    except Exception as error:
        print(f"{utils.Colors.White}{utils.Colors.Red}[YT.Downloads] [Error] {utils.Colors.White}DownloadError: {utils.Colors.Blue}Error Downloading Song: {error}{utils.Colors.White}")
    
    yield path

def albumDl(album: str):
    """Downloads an Album from search terms to a zip, and returns the zip.

    Args:
        album (str): The name of the album to download.
    """
    
    results = albumLookup(album)
    
    yield results[1], results[2], results[3]  # title, artist, errors

    filename = re.sub(r'[<>:"/\\|?*\']', '', f"{results[1]} - {results[2]}")

    try:
        paths = downloadSongs(results[0])
        zip = zipFolder(paths, 10**8, "TEMP/YTMusicZips", filename)
        for i in paths:
            os.remove(i)
    except Exception as error:
        #print(f"{utils.Colors.White}{utils.Colors.Red}[YT.Downloads] [Error] {utils.Colors.White}DownloadError: {utils.Colors.Blue}Error Downloading/Zipping Songs: {error}{utils.Colors.White}")
        pass
    yield zip
    
def dls(data: dict, client):
    """Send A Song or Multiple songs based on a seach term."""
    request = str(data['text'].lower()).removeprefix('!dls').strip()
    requestIsMulti = len(request.splitlines()) > 1
    
    if requestIsMulti:
        requests = request.splitlines()
        gen = multiSongDl(requests)
        songNames = next(gen)
        errors = next(gen)
        songstr = "*Now downloading:*"
        songNamesList = [
            f"\n{idx+1}. {song['title']} - {song['artist']}"
            for idx, song in enumerate(songNames)
        ]
        songstr += "".join(songNamesList)
        errs = [
            f"\n{idx+1}. {err}"
            for idx, err in enumerate(errors)
        ]
        if errors:
            songstr += "\n\n*The following requests errored:*" + "".join(errs) + "\n\n_Please check spelling or broaden search terms and try again for the errored items._"
        client.sendText(data['chatId'], songstr, {"quotedMsg":data['messageId']})
        path = next(gen)
        try:
            if len(path) == 1:
                client.sendFile(data["chatId"], path[0], {"quotedMsg":data['messageId']}, "SongZip", timeout=60*20)
                os.remove(path[0])
            else:
                for i in path:
                    # client.sendFile(data["chatId"], i, {"quotedMsg":data['messageId'], "caption":f"Zip {path.index(i)+1} of {len(path)}"}, "SongZip", timeout=60*20)
                    client.sendFile(data["chatId"], i, {"quotedMsg":data['messageId']}, "SongZip", timeout=60*20)
                for i in path:
                        os.remove(i)
                    
        except Exception as error:
            print(f"{utils.Colors.White}{utils.Colors.Red}[YT.Downloads] [Error] {utils.Colors.White}MultiSongSendError: {utils.Colors.Blue}Error Sending File: {error}{utils.Colors.White}")
    else:
        gen = singleSongDl(request)
        songName = next(gen)
        error = next(gen)

        if error:
            client.sendText(data['chatId'], f"*Error Occurred:* Please check spelling or broaden search terms and try again.", {"quotedMsg":data['messageId']})
            client.sendText(data['chatId'], f"*Error Details:* `{error[0]}`", {"quotedMsg":data['messageId']})
            return
        songStr = f"*Now downloading:* {songName['title']} - {songName['artist']}"
        client.sendText(data['chatId'], songStr, {"quotedMsg":data['messageId']})
        path = next(gen)
        try:
            client.sendFile(data["chatId"], path, {"quotedMsg":data['messageId'], "type":"document"}, "songFile", timeout=60*20)
            os.remove(path)
        except Exception as error:
            print(f"{utils.Colors.White}{utils.Colors.Red}[YT.Downloads] [Error] {utils.Colors.White}SingleSongSendError: {utils.Colors.Blue}Error Sending File: {error}{utils.Colors.White}")

def dla(data: dict, client):
    """Send an album based on a search term."""
    
    gen = albumDl(str(data['text'].lower()).removeprefix('!dla').strip())

    title, artist, errors = next(gen)
    
    if errors:
        client.sendText(data['chatId'], f"*Error Occurred:* Please check spelling or broaden search terms and try again.", {"quotedMsg":data['messageId']})
        client.sendText(data['chatId'], f"*Error Details:* `{errors}`", {"quotedMsg":data['messageId']})
        return
    
    songstr = f"*Now downloading:* {title} - {artist}"
    
    client.sendText(data['chatId'], songstr, {"quotedMsg":data['messageId']})

    path = next(gen)

    try:
        if len(path) == 1:
            client.sendFile(data["chatId"], path[0], {"quotedMsg":data['messageId']}, "AlbumZip", timeout=60*20)
            os.remove(path[0])
        else:
            for i in path:
                client.sendFile(data["chatId"], i, {"quotedMsg":data['messageId']}, "AlbumZip", timeout=60*20)
            for i in path:
                os.remove(i)
    except Exception as error:
        print(f"{utils.Colors.White}{utils.Colors.Red}[YT.Downloads] [Error] {utils.Colors.White}AlbumSendError: {utils.Colors.Blue}Error Sending File: {error}{utils.Colors.White}")
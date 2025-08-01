from ytmusicapi import YTMusic
from yt_dlp import YoutubeDL
from PIL import Image
import os, zipfile, BOT.utils as utils, concurrent.futures, subprocess, random

bannedchars = "<>:\"/\\|?*"

def zipFolder(path, maxSize=None, savePath="", name="Zipped"):
    """ 
    Returns A Number of zip file paths in a list
    if the size of the files in a folder is greater than maxSize, multiple Zip files are created.
    zip file paths are always returned in a list for consistency
    :param path: Required: provide the path to the folder of files to zip
    :param MaxSize: Optional: provide the maximum zip size in bytes, if None is specified, all files will be zipped in one file.
    :param savePath: Optional: Provide the path to save the file to. If none is specified, default to the location of the python script.
    :param name: Optional: Provide the name for the zip file. If none is specified, default to "Zipped"
    """
    if type(path) == str:
        filesInDir = os.listdir(path)
    else:
        filesInDir = path
    currentSize = 0
    zipnum=0
    fileListList = []
    fileList = []

    for file in filesInDir:
        if (currentSize + os.path.getsize(file)) > maxSize:
            fileListList.append(fileList)
            fileList = []
            currentSize = 0
        fileList.append(file)
        currentSize += os.path.getsize(file)
    fileListList.append(fileList)
    path = []
    with zipfile.ZipFile(f"{savePath}/{name}.zip", "w") as zipf:
        for i in fileListList:
            for j in i:
                if os.path.isfile(j):
                    arcname = os.path.basename(j)
                    zipf.write(j, arcname)
                    os.remove(j)
                else:
                    print(f"{utils.Colors.White}{utils.Colors.Red}[YT.Downloads] [Error] {utils.Colors.White}ZipError: {utils.Colors.Blue}Path: {j} does not exist. skipping...{utils.Colors.White}")
        path.append(f"{savePath}/{name}{zipnum}.zip")
    return path

music = YTMusic('BOT/YT/YtMusicAuth.json')

def songLookup(songs: list) -> tuple:
    """Uses the YT music search api to lookup songs and return a list. the first result in the tuple is the songs, and the second is the errors."""
    results = []
    errors = []
    
    def search(item):
        try:
            return music.search(item, filter='songs')
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

def downloadSongs(songList: list, outputDir: str="TEMP/YTMusicDownloads", maxWorkers: int=4):
    os.makedirs(outputDir, exist_ok=True)
    
    def download(song):
        url = f"https://music.youtube.com/watch?v={song['id']}"
        filename = f"{song['title']} - {song['artists']}.%(ext)s"
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
                    print(f"Error cropping thumbnail: {e}")

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
                    print(f"Error embedding thumbnail: {e}")
                            
        return audio_path

    with concurrent.futures.ThreadPoolExecutor(max_workers=maxWorkers) as executor:
        results = list(executor.map(download, songList))

    return results

def multiSongDl(songs: list):
    """Downloads Songs from search terms to a dir, and returns the dir.

    Args:
        songs (list): A list of Search terms as strings.
    """
    requestId = random.randint(100, 999)
    results = songLookup(songs)
    
    data = [{"title":i.get("title"), "artist":i.get("artists")} for i in results[0]]
    yield data
    yield results[1]
    
    try:
        paths = downloadSongs(results[0])
        zip = zipFolder(paths, 10**8, "TEMP/YTMusicZips", str(requestId))
    except Exception as error:
        print(error)
    
    yield zip

def dls(data: dict, client):
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

        print(1)
        path = next(gen)
        
        print(2)
        
        try:
            # client.sendFile(data["chatId"], path, {"quotedMsg":data['messageId'], 'filename':"Songs.zip"}, "", timeout=60*20)
            print(path, data['chatId'])
            client.sendFile(data["chatId"], path, {}, "ere", timeout=60*20)

        except Exception as error:
            print(error)
            
        print("Done")
        
        
        
    
    else:
        print("FUCK")
        requests = request
        client.sendFile(data["chatId"], "main.py", {}, "ere", timeout=60*20)
        # gen = songDl(request)
        
        songName = next(gen)










# Testing ground for new features and functions.
import time, asyncio

def test(data, client):
    try:
        from BOT.globals import main_loop
        loop = main_loop
        message = client.sendText(data.get("chatId"), "Test Number: 0")
        for i in range(1000):
            time.sleep(0.01)
            future = asyncio.run_coroutine_threadsafe(
                client.editMessage(message.get("id").removesuffix("_out"), f"Test Number: {str(i+1)}"),
                loop
            )
            future.result()
            
    except Exception as e: print(e)


from ytmusicapi import YTMusic
from yt_dlp import YoutubeDL
from PIL import Image
import os, zipfile, concurrent.futures, subprocess, uuid

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
    zipnum = 0
    if type(path) == str:
        filesInDir = os.listdir(path)
    else:
        filesInDir = path
    currentSize = 0
    fileListList = []
    fileList = []
    pathss = []

    for file in filesInDir:
        if (currentSize + os.path.getsize(file)) > maxSize:
            fileListList.append(fileList)
            fileList = []
            currentSize = 0
        fileList.append(file)
        currentSize += os.path.getsize(file)
    fileListList.append(fileList)
    path = []
    for i in fileListList:
        zipnum += 1
        if not os.path.exists(f"{savePath}"):
            os.mkdir(f"{savePath}")
        with zipfile.ZipFile(f"{savePath}\\{name}{zipnum}.zip", "a", compression=zipfile.ZIP_DEFLATED) as zipf:
            for j in i:
                if os.path.isfile(j):
                    arcname = j[j.rfind("\\")+1:]
                    zipf.write(j, arcname)
                    os.remove(j)
                else:
                    pass
                    # print(f"{utils.Colors.White}{utils.Colors.Red}[YT.Downloads] [Error] {utils.Colors.White}ZipError: {utils.Colors.Blue}Path: {j} does not exist. skipping...{utils.Colors.White}")
        path.append(f"{savePath}\\{name}{zipnum}.zip")
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

def downloadSongs(songList: list, outputDir: str="TEMP\\YTMusicDownloads", maxWorkers: int=4):
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
    requestId = uuid.uuid4()
    results = songLookup(songs)
    
    data = [{"title":i.get("title"), "artist":i.get("artists")} for i in results[0]]
    yield data
    yield results[1]
    
    paths = downloadSongs(results[0])
    
    zip = zipFolder(paths, 10**8, "TEMP/YTMusicZips", str(requestId))
    
    yield zip





if __name__ == "__main__":
    songs = ["steel Commanders", "viva la vida", "in place of your halo"]

    gen = multiSongDl(songs)
    
    print(next(gen))
    print(next(gen))
    print(next(gen))
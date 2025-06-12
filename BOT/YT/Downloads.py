from ytmusicapi import YTMusic
import yt_dlp, os, zipfile, BOT.utils as utils, concurrent.futures

import time
from WPP_Whatsapp import Create # REMOVE, for reference only

# client = Create().start() # REMOVE, for reference only

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
    filesInDir = os.listdir(path)
    currentSize = 0
    fileListList = []
    fileList = []
    pathss = []
    for i in filesInDir:
        if i[-4:].lower() == '.mp3':
            pathss.append(os.path.join(path, i))

    for file in pathss:
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
                    print(f"{utils.Colors.White}{utils.Colors.Red}[YT.Downloads] [Error] {utils.Colors.White}ZipError: {utils.Colors.Blue}Path: {j} does not exist. skipping...{utils.Colors.White}")
        path.append(f"{savePath}\\{name}{zipnum}.zip")
    return path

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

def songDl(searchTerm: str) -> str:
    """Downloads a single song from a search result and returns the file path.

    Args:
        searchTerm (str): The Search Term To use.

    Returns:
        str: The path of the downloaded song. 
    """
    
def multiSongDl(songs: list):
    """Downloads Songs from search terms to a dir, and returns the dir.

    Args:
        songs (list): A list of Search terms as strings.
    """
    time.sleep(1)
    songLookup([])
    yield [{"title":"Song1", "artName":"Art1"}, {"title":"Song2", "artName":"Art2"}, {"title":"Song3", "artName":"Art3"}]
    yield [i for i in songs]
    yield "Testv2.zip"
    pass



def dls(data: dict, client):
    songLookup([])
    request = str(data['text']).removeprefix('!dls').strip()
    requestIsMulti = len(request.splitlines()) > 1
    
    if requestIsMulti:

        requests = request.splitlines()
        gen = multiSongDl(requests)

        songNames = next(gen)
        errors = next(gen)

        songstr = "*Now downloading:*"
        songNamesList = [
            f"\n{idx+1}. {song['title']} - {song['artName']}"
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
        
        # zipPath = zipFolder(path, 100000000, path, "Zip")
        
        print("eeee")
        
        # client.sendFile(data["chatId"], path, {"quotedMsg":data['messageId'], 'filename':"Songs.zip"}, timeout=60*20)
        client.sendFile(data["chatId"], path, {"quotedMsg":data['messageId'], 'filename':"Songs.zip"}, f"{path}", timeout=60*20)
        
        print("bbbb")

        
        
        
    
    else:
        requests = request
        gen = songDl(request)
        
        songName = next(gen)










# BRIAN V2!
Brian is a lil chatbot for whatsapp that i created to learn how to code... this is the second iteration of that, with better structure to the code and an easier way of doing things. 

## What can Brian do?
Brian is a chatbot that can run on a normal whatsapp account (no shitty meta BS involved)

### He can currently:
 - Download songs & albums
 - AI chat with brian
 - Random other commands and features probably ehhh

## Where is Brian v1?
Why would you even want to know that you sick bastard

## Installing

Clone the repo, then `cd` into it.  

### 1. Create a virtual environment

```bash
# Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell or CMD)
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install requirements

```bash
# Linux
python3 -m pip install -r requirements.txt

# Windows
python -m pip install -r requirements.txt
```

### 3. Install Playwright drivers

```bash
# Linux (first install system dependencies, then browsers)
playwright install-deps
playwright install

# Windows (you may need to run terminal as Administrator)
playwright install
```

### 4. Install ffmpeg (required for song features)

Download from [ffmpeg.org/download](https://ffmpeg.org/download.html) and follow the install instructions for your OS.  


### 5. Cookie setup

#### yt-dlp
Follow the [yt-dlp cookies export guide](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies).  
Save the exported file as:

```
./BOT/YT/ytdlp-cookies.txt
```

#### ytMusicAPI
Follow the [ytmusicapi OAuth setup](https://ytmusicapi.readthedocs.io/en/stable/setup/oauth.html).  
Save the exported file as:

```
./BOT/YT/YtMusicAuth.json
```

### 6. API keys

Create a file at:

```
./keys.env
```

Contents:

```
OPENAI_API_KEY=sk-proj-xxxxxx...
```

This step is only required for chat with the AI.

### 7. Running Brian

```bash
# Linux
python3 main.py

# Windows
python main.py
```

On first run:
- Data files will be created automatically.  
- Add your number to `./admins.txt` in this format:

```
61412345678@c.us
```

(`61` = country code, `@c.us` is mandatory).  

- Scan the QR code shown in terminal using **Linked Devices** on your phone.  
- If successful, you’ll get a message:

```
Brian started successfully!
```

Run `!help` in chat to see admin commands.  

### Enjoy using Brian!

## To-do:
### Features:
 - ~~Song Downloader~~
 - ~~Album Downloader~~
 - AI image generator
 - ~~ChatGPT chat (BrAIn)~~
 - Text to Shakespeare
### General:
 - JSON file for all the stuff that is currently kept in .txt files.
 - ~~Back-and-forth chatting. (eg the bot asks "are you sure you want to procede?")~~
 - ~~Put it on a server~~

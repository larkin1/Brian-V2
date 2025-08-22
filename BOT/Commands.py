import BOT.YT.Downloads as Downloads
import BOT.help as help
import BOT.adminCmds as adminCmds
import BOT.testfuncts as testfuncts
import BOT.session as session
import BOT.AI.openai as brainai
# This file contains the command mappings for the bot.
# Each command is associated with a function that will be executed when the command is called.
# For each command, the first element is the function to call, the second element is a list of help messages, and the third is a short descriptor string.
# Help messages are send individually one by one to the user when they request help for a specific command.

userCommands = {
    "help": (help.help, 
        ["Aight bro, why did you even do this one?"],
        "Helper Command"
    ),

    "dls": (Downloads.dls, 
        [
            "Function to download songs. Uses Youtube search algorithms to find your song.", 
            "To download a song, simply do ```!dls <song name>```\nFor multiple songs, simply add a line break for each new song."
        ],
        "Download a song."
    ),

    "dla": (Downloads.dla, 
        [
            "Function to download albums. Uses Youtube search algorithms to find your album.", 
            "To download an album, simply do ```!dla <album name>```"
        ],
        "Download an album."
    ),

    "lss": (Downloads.lss, 
        [
            "Function to search for songs. Uses Youtube search algorithms to find your song.", 
            "To search for a song, simply do ```!lss <song name>```"
        ],
        "Search for a song."
    ),
    
    "lsa": (Downloads.lsa, 
        [
            "Function to search for albums. Uses Youtube search algorithms to find your album.", 
            "To search for an album, simply do ```!lsa <album name>```"
        ],
        "Search for an album."
    ),

    "brain": (brainai.brain,
        [
            "Start an AI chat session. Use `!brain` to start, then chat normally. Use `!exit` to stop.",
            "Remembers the last 20 messages in this chat. Supports quoted messages and shows usernames."
        ],
        "AI Chat (Brain)"
    ),

    "test": (testfuncts.test, 
        [
            "Test"
        ],
        "Test"
    ),

    "exit": (session.exit_command,
        [
            "Exit the current streaming mode started by a command."
        ],
        "Exit stream mode."
    ),
}

adminCommands = userCommands.copy()

adminCommands.update({
    "whitelist": (adminCmds.whitelist, 
        [
            "Adds a user or chat to the whitelist."
        ],
        "Admin Only Command"
    ),
    
    "ban": (adminCmds.ban, 
        [
            "Bans a user or chat from using the bot."
        ],
        "Admin Only Command"
    ),
    
    "admintest": (testfuncts.adminTest, 
        [
            "Admin Only Command"
        ],
        "Admin Only Command"
    ),
})

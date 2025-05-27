import YT.Downloads, AI.musicgen, testfuncts, RESOURCES.help
# This file contains the command mappings for the bot.
# Each command is associated with a function that will be executed when the command is called.
# For each command, the first element is the function to call, and the second element is a list of help messages.
# Help messages are send individually one by one to the user when they request help for a specific command.

commands = {
    "help": (RESOURCES.help.help, 
        ["Aight bro, why did you even do this one?"]),

    "song": (YT.Downloads.song, 
        ["Downloads a song from YouTube.",
        "Usage: !song <YouTube URL>",
        "Example: !song https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "Returns: A downloaded song file."]),

    "musicgen": (AI.musicgen.musicgen, 
        ["Generates a song using AI.",
        "Usage: !musicgen <prompt> <duration> <lyrics>",
        "Example: !musicgen 'A happy song' 30 'Happy lyrics'",
        "Returns: A generated song file."]),
    
    "test": (testfuncts.test, 
        ["Spams"]),
}

import YT.Downloads, AI.musicgen, testfuncts, RESOURCES.help
# This file contains the command mappings for the bot.
# Each command is associated with a function that will be executed when the command is called.
# For each command, the first element is the function to call, and the second element is a list of help messages.
# Help messages are send individually one by one to the user when they request help for a specific command.

commands = {
    "help": (RESOURCES.help.help, 
        ["Aight bro, why did you even do this one?"]),

    "song": (YT.Downloads.song, 
        ["NOT CURRENTLY IMPLEMENTED",]),

    "musicgen": (AI.musicgen.musicgen, 
        ["NOT CURRENTLY IMPLEMENTED",]),

    "test": (testfuncts.test, 
        ["Spams"]),
}
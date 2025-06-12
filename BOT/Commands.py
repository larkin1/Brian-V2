import BOT.YT.Downloads as Downloads, BOT.AI.musicgen as musicgen, BOT.help as help, BOT.adminCmds as adminCmds, BOT.testfuncts as testfuncts
# This file contains the command mappings for the bot.
# Each command is associated with a function that will be executed when the command is called.
# For each command, the first element is the function to call, the second element is a list of help messages, and the thirs is a short descriptor string.
# Help messages are send individually one by one to the user when they request help for a specific command.

userCommands = {
    "help": (help.help, 
        ["Aight bro, why did you even do this one?"],
        "Helper Command"),

    "ds": (Downloads.dls, 
        ["NOT CURRENTLY IMPLEMENTED",],
        "Download a song."),

    "musicgen": (musicgen.musicgen, 
        ["NOT CURRENTLY IMPLEMENTED",],
        "Generate music using AI."),

    "test": (testfuncts.test, 
        ["Test"],
        "Text"),
}

adminCommands = userCommands.copy()
adminCommands.update({
    "whitelist": (adminCmds.whitelist, 
        ["Adds a user or chat to the whitelist."],
        "Admin Only Command"),
    "ban": (adminCmds.ban, 
        ["Bans a user or chat from using the bot."],
        "Admin Only Command"),
})

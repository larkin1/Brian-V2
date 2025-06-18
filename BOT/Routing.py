from BOT.Commands import userCommands, adminCommands
import BOT.utils as utils, BOT.exeQueue as exeQueue
# This file contains the routing logic for commands in the bot.

def route_command(text: str, chat: str, skip_whitelist_check: bool, *args, **kwargs):
    """
    Routes the command to the appropriate function based on the command name.
    """

    whitelist = open("BOT/Whitelist.txt", "r").read().splitlines()

    if skip_whitelist_check:
        for i in adminCommands: # Iterate through the commands dictionary and run the command if it matches any of the keys
            if text.lower().startswith(f"!{i}"):
                exeQueue.addItem(adminCommands[i][0], *args, **kwargs)
                return

    elif chat in whitelist:
        for i in userCommands: # Iterate through the commands dictionary and run the command if it matches any of the keys
            if text.lower().startswith(f"!{i}"):
                exeQueue.addItem(userCommands[i][0], *args, **kwargs)
                return

    print(f"{utils.Colors.White}{utils.Colors.Red}[Error] {utils.Colors.White}{"System"}: {utils.Colors.Blue}{"Command Not Found!"}{utils.Colors.White}")
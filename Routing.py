from RESOURCES.Commands import userCommands, adminCommands
import utils
# This file contains the routing logic for commands in the bot.

def route_command(text: str, chat: str, skip_whitelist_check: bool, *args, **kwargs):
    """
    Routes the command to the appropriate function based on the command name.
    """

    whitelist = open("RESOURCES/Whitelist.txt", "r").read().splitlines()

    if skip_whitelist_check:
        for i in adminCommands: # Iterate through the commands dictionary and run the command if it matches any of the keys
            if text.startswith(f"!{i}"):
                return adminCommands[i][0](*args, **kwargs)
            
    elif chat in whitelist:
        for i in userCommands: # Iterate through the commands dictionary and run the command if it matches any of the keys
            if text.startswith(f"!{i}"):
                return userCommands[i][0](*args, **kwargs)

    print(f"{utils.Colors.White}{utils.Colors.Red}[Error] {utils.Colors.White}{"System"}: {utils.Colors.Blue}{"Command Not Found!"}{utils.Colors.White}")
from RESOURCES.Commands import commands
import utils
# This file contains the routing logic for commands in the bot.

def route_command(text: str, chat: str, skip_whitelist_check: bool, *args, **kwargs):
    """
    Routes the command to the appropriate function based on the command name.
    """

    whitelist = open("RESOURCES/Whitelist.txt", "r").read().splitlines()

    if skip_whitelist_check or chat in whitelist:
        for i in commands: # Iterate through the commands dictionary and run the command if it matches any of the keys
            if text.startswith(f"!{i}"):
                return commands[i][0](*args, **kwargs)

    print(f"{utils.Colors.White}{utils.Colors.Red}[Error] {utils.Colors.White}{"System"}: {utils.Colors.Blue}{"Command Not Found!"}{utils.Colors.White}")
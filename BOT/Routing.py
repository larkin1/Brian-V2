from BOT.Commands import userCommands, adminCommands
from BOT.utils import Colors
import BOT.exeQueue as exeQueue
# This file contains the routing logic for commands in the bot.

def route_command(
    text: str, 
    chat: str, 
    skip_whitelist_check: bool, 
    *args, **kwargs
):
    """
    Routes the command to the appropriate function based on the command name.
    """

    try:
        whitelist = open("Whitelist.txt", "r").read().splitlines()
    except FileNotFoundError:
        # Create the file if it doesn't exist
        open("Whitelist.txt", "w").close()
        whitelist = []

    if skip_whitelist_check:
        # run the command if it matches any of the keys
        for i in adminCommands: 
            if text.lower().startswith(f"!{i}"):
                exeQueue.addItem(adminCommands[i][0], *args, **kwargs)
                return

    elif chat in whitelist:
        for i in userCommands: 
            # run the command if it matches any of the keys
            if text.lower().startswith(f"!{i}"):
                exeQueue.addItem(userCommands[i][0], *args, **kwargs)
                return
    
    error_message = (
        f"{Colors.Red}[Error] "
        f"{Colors.White}System: "
        f"{Colors.Blue}Command Not Found!{Colors.White}"
    )
    print(error_message)
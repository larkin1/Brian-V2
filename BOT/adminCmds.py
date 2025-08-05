def whitelist(data, client):
    """Adds a user or chat to the whitelist."""
    chat = data["chatId"]
    Number = data["text"].removeprefix("!whitelist").strip()

    if Number:
        chat = Number

    

    whitelistData = open("BOT/Whitelist.txt", "r")
    whitelistClean = [i.strip().strip("\n") for i in whitelistData.readlines()]
    whitelistData.close()
    whitelist = open("BOT/Whitelist.txt", "a")
    if str(chat) not in whitelistClean:
        whitelist.write(f"{chat}\n")
        client.sendText(chat, f"Added `{chat}` to the Whitelist!")
    else:
        client.sendText(chat, f"`{chat}` Already In whitelist!")
    whitelist.close()

def ban(data, client):
    """Bans a user or chat from the bot."""
    chat = data["text"].removeprefix("!ban").strip()
    
    whitelist = open("BOT/Whitelist.txt", "r")
    lines = whitelist.readlines()
    whitelist.close()
    
    with open("BOT/Whitelist.txt", "w") as whitelist:
        for line in lines:
            if line.strip().strip("\n") != chat:
                whitelist.write(line)
    
    client.sendText(chat, f"Removed `{chat}` from the Whitelist!")
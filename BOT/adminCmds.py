def whitelist(data, client):
    """Adds one or more users/chats to the whitelist."""
    # Remove the command prefix and strip whitespace
    entries = data["text"].removeprefix("!whitelist").strip()

    # If there are multiple lines, treat each as a separate entry
    if entries:
        to_add = [e.strip() for e in entries.splitlines() if e.strip()]
    else:
        # If no argument, default to the sender's chatId
        to_add = [data["chatId"]]

    # Read the current whitelist
    try:
        with open("BOT/Whitelist.txt", "r") as whitelistData:
            whitelistClean = [i.strip().strip("\n") for i in whitelistData.readlines()]
    except FileNotFoundError:
        whitelistClean = []
        open("BOT/Whitelist.txt", "w").close()

    added = []
    already = []
    with open("BOT/Whitelist.txt", "a") as whitelist:
        for entry in to_add:
            if entry and entry not in whitelistClean:
                whitelist.write(f"{entry}\n")
                added.append(entry)
            elif entry:
                already.append(entry)

    # Send feedback messages
    if added:
        client.sendText(data["chatId"], f"Added to Whitelist: {', '.join(f'`{a}`' for a in added)}")
    if already:
        client.sendText(data["chatId"], f"Already in Whitelist: {', '.join(f'`{a}`' for a in already)}")

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
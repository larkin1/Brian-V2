import re

def whitelist(data, client):
    """Adds one or more users/chats to the whitelist."""
    # Remove the command prefix and strip whitespace
    entries = data["text"].removeprefix("!whitelist").strip()

    # If there are multiple lines, treat each as a separate entry
    if entries:
        raw_entries = [e.strip() for e in entries.splitlines() if e.strip()]
    else:
        raw_entries = [data["chatId"]]

    to_add = []
    for entry in raw_entries:
        # If entry looks like a number (not already a full WhatsApp ID), format it
        if entry.isdigit() or (re.sub(r'\D', '', entry) == entry and not entry.endswith('@c.us')):
            num = re.sub(r'\D', '', entry)
            if num:
                entry = num + '@c.us'
        elif not entry.endswith('@c.us') and entry.isnumeric() == False:
            # If it's not a number and not ending with @c.us, leave as is
            pass
        to_add.append(entry)

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
    """Bans one or more users/chats from the bot."""
    entries = data["text"].removeprefix("!ban").strip()

    # If there are multiple lines, treat each as a separate entry
    if entries:
        raw_entries = [e.strip() for e in entries.splitlines() if e.strip()]
    else:
        raw_entries = [data["chatId"]]

    to_remove = []
    for entry in raw_entries:
        # If entry looks like a number (not already a full WhatsApp ID), format it
        if entry.isdigit() or (re.sub(r'\D', '', entry) == entry and not entry.endswith('@c.us')):
            num = re.sub(r'\D', '', entry)
            if num:
                entry = num + '@c.us'
        elif not entry.endswith('@c.us') and entry.isnumeric() == False:
            # If it's not a number and not ending with @c.us, leave as is
            pass
        to_remove.append(entry)

    # Read the current whitelist
    try:
        with open("BOT/Whitelist.txt", "r") as whitelistData:
            whitelistClean = [i.strip().strip("\n") for i in whitelistData.readlines()]
    except FileNotFoundError:
        whitelistClean = []
        open("BOT/Whitelist.txt", "w").close()

    removed = []
    not_found = []
    # Remove entries from the whitelist
    new_whitelist = [w for w in whitelistClean if w not in to_remove]
    for entry in to_remove:
        if entry in whitelistClean:
            removed.append(entry)
        else:
            not_found.append(entry)
    # Write updated whitelist
    with open("BOT/Whitelist.txt", "w") as whitelist:
        for w in new_whitelist:
            whitelist.write(w + "\n")

    # Send feedback messages
    if removed:
        client.sendText(data["chatId"], f"Removed from Whitelist: {', '.join(f'`{a}`' for a in removed)}")
    if not_found:
        client.sendText(data["chatId"], f"Not found in Whitelist: {', '.join(f'`{a}`' for a in not_found)}")
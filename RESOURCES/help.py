# Help Command. Routes appropriate help messages to the user.

def help(data, client):
    """Sends a help message to the user."""
    from RESOURCES.Commands import commands

    if data["text"].lower().strip() == "!help":
        commandList = "".join([i+"\n" for i in commands.keys()]).strip("\n")

        text = f"""Hi, I'm Brian,
To view the details and usage of a specific command, type !help <command_name>

{commandList}
"""
        client.sendText(data['chatId'], text)
    else:
        command = data["text"].lower().removeprefix("!help ").strip()
        if command in commands.keys():
            for i in commands[command][1]:
                client.sendText(data["chatId"], i)
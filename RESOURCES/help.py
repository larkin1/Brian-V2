# Help Command. Routes appropriate help messages to the user.

def help(data, client):
    """Sends a help message to the user."""
    from RESOURCES.Commands import commands

    if data["text"].lower().strip() == "!help":
        commandList = "\n".join(
            f"- `!{i}`: _{commands[i][2]}_" if len(commands[i]) > 2 and commands[i][2] 
            else f"`!{i}`" for i in commands
        )

        text = f"""*Hi, I'm Brian II (The second)*
        
To learn more about a command and how to use it, type:
`!help <command_name>`

*Available commands:*

{commandList}
"""
        client.sendText(data['chatId'], text)
    else:
        command = data["text"].lower().removeprefix("!help ").strip()
        if command in commands.keys():
            for i in commands[command][1]:
                client.sendText(data["chatId"], i)
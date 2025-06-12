# Help Command. Routes appropriate help messages to the user.

def help(data, client):
    """Sends a help message to the user."""
    from BOT.Commands import userCommands

    if data["text"].lower().strip() == "!help":
        commandList = "\n".join(
            f"- `!{i}`: _{userCommands[i][2]}_" if len(userCommands[i]) > 2 and userCommands[i][2] 
            else f"`!{i}`" for i in userCommands
        )

        text = f"""*Hi, I'm Brian II (The second)*
        
To learn more about a command and how to use it, type:
`!help <Command name>`

*Available commands:*

{commandList}
"""
        client.sendText(data['chatId'], text)
    else:
        command = data["text"].lower().removeprefix("!help ").strip()
        if command in userCommands.keys():
            for i in userCommands[command][1]:
                client.sendText(data["chatId"], i)
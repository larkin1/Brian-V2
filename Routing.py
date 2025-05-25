from Commands import commands
## Funct to call when a command is received

def route_command(command: str, *args, **kwargs):
    """
    Routes the command to the appropriate function based on the command name.
    """
    # Check if the command exists in the commands dictionary
    if command in commands:
        return commands[command](*args, **kwargs)
    else:
        raise ValueError(f"Command '{command}' not found.")
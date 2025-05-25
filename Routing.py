from Commands import commands

def route_command(text: str, *args, **kwargs):
    """
    Routes the command to the appropriate function based on the command name.
    """

    if not text.startswith("!"): # Ensure the command starts with '!'
        raise ValueError("Command must start with '!'")
    
    for i in commands: # Iterate through the commands dictionary and run the command if it matches any of the keys
        if text.startswith(f"!{i}"):
            return commands[i](*args, **kwargs)
        
    raise ValueError(f"Command not found.") # This will raise an error if the command is not found in the commands dictionary.
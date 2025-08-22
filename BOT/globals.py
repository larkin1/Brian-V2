main_loop = None
client = None

with open("admins.txt", "r") as file:
    Admins = [line.strip() for line in file if line.strip()]
import time
# Testing ground for new features and functions.

def test(data, client):
    for i in data["raw"]:
        print(f"{i}: {data["raw"][i]}")

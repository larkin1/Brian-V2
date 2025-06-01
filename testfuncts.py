# Testing ground for new features and functions.
import time

def test(data, client):
    time.sleep(2)
    client.sendText('REDACTED@c.us', "eeee")
    time.sleep(10)
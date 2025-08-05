# Testing ground for new features and functions.
import time, asyncio

def test(data, client):
    client.sendText(data['chatId'], data['authorId'])
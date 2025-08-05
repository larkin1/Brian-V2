# Testing ground for new features and functions.
import time, asyncio

def test(data, client):
    client.sendText(data['chatId'], f"Author Id: ```{data['authorId']}```\nChat Id: ```{data['chatId']}```")

def adminTest(data, client):
    client.sendText(data['chatId'], f"*ADMIN TEST*\nAuthor Id: ```{data['authorId']}```\nChat Id: ```{data['chatId']}```")
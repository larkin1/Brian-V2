import time
# Testing ground for new features and functions.

def test(data, client):
    for i in range(1):
        for i in range(10):
            client.sendText(data['chatId'], f"Wow, Crazy")
        time.sleep(0.1)

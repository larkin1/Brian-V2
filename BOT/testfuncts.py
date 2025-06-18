# Testing ground for new features and functions.
import time, asyncio

def test(data, client):
    try:
        from BOT.globals import main_loop
        loop = main_loop
        message = client.sendText(data.get("chatId"), "Test Number: 0")
        for i in range(1000):
            time.sleep(0.01)
            future = asyncio.run_coroutine_threadsafe(
                client.editMessage(message.get("id").removesuffix("_out"), f"Test Number: {str(i+1)}"),
                loop
            )
            future.result()
            
    except Exception as e: print(e)
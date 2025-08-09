# Testing ground for new features and functions.
import time, asyncio
import BOT.session as session


def _mirror_handler(data, client):
    """Mirror handler: echoes every non-command message in the active chat."""
    txt = data.get("text")
    if not txt:
        return
    # Only mirror non-commands; commands are handled by router before this.
    session.suppress_next(data['chatId'], txt)
    client.sendText(data['chatId'], txt)


def test(data, client):
    """Enter mirror stream mode for this chat until !exit is received."""
    session.enter_stream(data['chatId'], _mirror_handler, name="mirror")
    notice = (
        "Mirror mode enabled. Send messages and I'll echo them. Send !exit to stop.\n"
        f"Author Id: ```{data['authorId']}```\nChat Id: ```{data['chatId']}```"
    )
    session.suppress_next(data['chatId'], notice)
    client.sendText(data['chatId'], notice)


def adminTest(data, client):
    client.sendText(data['chatId'], f"*ADMIN TEST*\nAuthor Id: ```{data['authorId']}```\nChat Id: ```{data['chatId']}```")
import time
import asyncio

import BOT.session as session

# Testing ground for new features and functions.


def _mirror_handler(data, client):
    """Mirror handler: echoes every non-command message in the active chat."""
    
    txt = data.get("text")
    if not txt:
        return
    
    # Only mirror non-commands; commands are handled by router before this.
    session.suppress_next(data["chatId"], txt)
    client.sendText(data["chatId"], txt)

Messages = [
    """Hi!, this is an automated string of messages.
    You are recieving these message because you are on Brian's whitelist.""",
    """This notification is to inform you that Brian is being retired.""",
    """*General info*:
    Brian will be turned off at some point in the next couple of days (probably wed arvo AU time). This means you will have a brief time to download songs before Brian is turned off completely.
    Probably don't download your songs super soon after seeing this message... If everyone tries to at once, i fear Brian may come to a swifter end 😅
    Brian's source code is available on github. If you don't have experience with this sort of thing, you won't have much, if any luck with getting it to work, and I don't really feel like providing support for it. In it's current state it is not only unreliable and broken (as I'm sure you may know), but also quite difficult to actually set up.
    for futher inquires please message me (if you send a request to the bot after you message me i WON'T see your messaage.)"""
    """Brian has been a fun project that i have genuinley enjoyed working on (despite my gripes), and i believe that it is best for it to come to it's natural concluision rather than an unnatural one (specifically one that involves trouble).""",
]


def test(data, client):
    """Enter mirror stream mode for this chat until !exit is received."""
    for i in Messages:
        client.sendText(data["chatId"], i)


def adminTest(data, client):
    
    whitelist = open("Whitelist.txt", "r").read().splitlines()

    for i in whitelist:
        for j in Messages:
            client.sendText(f"{i}@c.us", j)

    client.sendText(data["chatId"], f"*ADMIN TEST*\nAuthor Id: ```{data["authorId"]}```\nChat Id: ```{data["chatId"]}```")
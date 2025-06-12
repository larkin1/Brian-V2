# Utilities for the bot.

class Colors:
    """Class of ALL the colors used in the console output."""
    Default = "\x1b[39m"
    Black = "\x1b[30m"
    Red = "\x1b[31m"
    Green = "\x1b[32m"
    Yellow = "\x1b[33m"
    Blue = "\x1b[34m"
    Magenta = "\x1b[35m"
    Cyan = "\x1b[36m"
    LightGray = "\x1b[37m"
    DarkGray = "\x1b[90m"
    LightRed = "\x1b[91m"
    LightGreen = "\x1b[92m"
    LightYellow = "\x1b[93m"
    LightBlue = "\x1b[94m"
    LightMagenta = "\x1b[95m"
    LightCyan = "\x1b[96m"
    White = "\x1b[97m"

def printMessage(message, user, username):
    """
    Prints the message to the console with color coding based on whether the user is a user or not.
    """
    if message:
        whitelist = open("BOT/Whitelist.txt", "r").read().splitlines()
        if user not in whitelist:
            if message[0] == "!":
                print(f"{Colors.White}{(f"{Colors.Red}[Command] {Colors.White}" + username + ':')} {Colors.Blue}{message}{Colors.White}")
            else:
                print(f"{Colors.White}{(f"{Colors.Yellow}[Message] {Colors.White}" + username + ':')} {Colors.Blue}{message}{Colors.White}")
        else:
            if message[0] == "!":
                print(f"{Colors.White}{(f"{Colors.Red}[Command] {Colors.Cyan}[User] {Colors.White}" + username + ':')} {Colors.Blue}{message}{Colors.White}")
            else:
                print(f"{Colors.White}{(f"{Colors.Yellow}[Message] {Colors.Cyan}[User] {Colors.White}" + username + ':')} {Colors.Blue}{message}{Colors.White}")

def getMessageData(msg):
    """Fetches and returns the message data from the received message."""
    message = msg['data']
    try:text = message['text']
    except:text = None
    authorId = message['author']
    chatId = message['chatId']
    messageId = message['id']
    senderName = message['sender']['name']

    hasQuote = False
    if 'quotedMsgObj' in message:
        hasQuote = True
        quotedMessage = msg['data']['quotedMsgObj']
        try:quotedText = quotedMessage['text']
        except:quotedText = None
        quotedAuthorId = quotedMessage['author']
        quotedChatId = quotedMessage['chatId']
        quotedMessageId = quotedMessage['id']
        quotedSenderName = quotedMessage['sender']['name']
    
    data = {
        'raw': msg,
        'text': text,
        'authorId': authorId,
        'chatId': chatId,
        'messageId': messageId,
        'senderName': senderName,
        'hasQuote': False
    }

    if hasQuote:
        data['hasQuote'] = True
        data['quotedText'] = quotedText
        data['quotedAuthorId'] = quotedAuthorId
        data['quotedChatId'] = quotedChatId
        data['quotedMessageId'] = quotedMessageId
        data['quotedSenderName'] = quotedSenderName

    return data

def printCode(code):
    print(code)

import qrterm
def catchQR(qrCode: str, asciiQR: str, attempt: int, urlCode: str):
    """Catches a QR code and prints it to the console."""
    qrterm.draw(urlCode)
    # for line in asciiQR.splitlines():
    #     print(line)
        
def newGetMessageData(msg):
    """Fetches and returns the message data from the received message."""
    
    text = msg.get("body")
    authorId = msg.get("sender").get("id").get("_serialized")
    authorName = msg.get("sender").get("name")
    chatId = msg.get("chatId").get("_serialized")
    messageId = msg.get("id")
    
    hasQuote = False
    if msg.get("quotedMsg"):
        hasQuote = True
        quotedText = msg.get("quotedMsg").get("body")
        quotedMessageId = msg.get("quotedMsgId")    
        quotedparticipant = msg.get("quotedParticipant")
        try:
            quotedChatId = quotedMessageId.split("_")[1]
        except:
            quotedChatId = None
    
    data = {
        'raw': msg,
        'text': text,
        'authorId': authorId,
        'authorName': authorName,
        'chatId': chatId,
        'messageId': messageId,
        'hasQuote': False
    }

    if hasQuote:
        data['hasQuote'] = True
        data['quotedText'] = quotedText
        data['quotedMessageId'] = quotedMessageId
        data['quotedParticipant'] = quotedparticipant
        data['quotedChatId'] = quotedChatId
    
    return data
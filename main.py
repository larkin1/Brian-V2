import BOT.utils as utils, BOT.Routing as Routing, BOT.DbMgmt as DbMgmt, datetime, time, threading, BOT.exeQueue as exeQueue
from WPP_Whatsapp import Create

# brian\scripts\activate

MyNumber = 'REDACTED@c.us'
MyNumbers = ['REDACTED@c.us', 'REDACTED@lid']

creator = Create(session="brianv2", browser='chrome', headless=True, catchQR=utils.catchQR, logQR=True, qr='terminal')
client = creator.start()

def handle_new_message(msg):
    """Function to handle new messages received by the client."""
    global client
    
    if str(msg.get("chatId").get("_serialized")) != "status@broadcast" and msg.get("body"): # checking that the message is valid and not a status message
        # Get the data into a more useable dict.
        data = utils.newGetMessageData(msg)

        # Save the message to the database (if the database is already in use, it retries up to 10 times with a backoff).
        try:
            DbMgmt.saveRecord(data['chatId'], datetime.datetime.now(datetime.UTC).timestamp(), data['text'], data['authorId'])
        except:
            for i in range(10):
                try:
                    DbMgmt.saveRecord(data['chatId'], datetime.datetime.now(datetime.UTC).timestamp(), data['text'], data['authorId'])
                    break
                except: time.sleep(i)

        # Print the message using the correct format, depending on user status and other variables
        utils.printMessage(data['text'], data['authorId'], data['authorName'])

        chat = data["chatId"]

        skipCheck = str(data['authorId']) in MyNumbers # If it's the admin, skip the whitelist check.
        
        # If the message is a suspected comand...
        if data["text"][0] == "!":
            try:
                Routing.route_command(data['text'], chat, skipCheck, data, client)
            except Exception as e:
                print(f"{utils.Colors.White}{utils.Colors.Red}[Error] {utils.Colors.White}{e.__class__.__name__}: {utils.Colors.Blue}{e}{utils.Colors.White}")

if creator.state != 'CONNECTED':
    raise Exception(creator.state)

executor = threading.Thread(target=exeQueue.jobProcessor).start()

print("Initialised the client successfully!")

client.sendText(MyNumber, "Brian (v2) started successfully!")

# Add Listen To New Message
creator.client.onAnyMessage(handle_new_message)
creator.loop.run_forever()
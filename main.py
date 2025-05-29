debug_mode = input("Start in Debug mode? (y/n): ") # I put this up here to make it show up faster becasue i'm impatient.
from wa_automate_socket_client import SocketClient
import utils, Routing, DbMgmt, datetime

if debug_mode.lower().strip() == "y":
    debug_mode = True
else: 
    debug_mode = False

MyNumber = 'REDACTED@c.us'
client = SocketClient('http://localhost:8085/', 'secure_api_key') # YOU HAVE TO RUN EASY API BEFORE THIS IS CALLED (and i don't know how to run it from this script hehe)

def handle_new_message(msg):
    # Get the data into a more useable dict.
    data = utils.getMessageData(msg)

    # Save the message to the database
    DbMgmt.saveRecord(data['chatId'], datetime.datetime.now(datetime.UTC).timestamp(), data['text'], data['authorId'])

    # Print the message using the correct format, depending on user status and other variables
    utils.printMessage(data['text'], data['authorId'], data['senderName'])
    
    # If the message is a suspected comand...
    if data["text"][0] == "!":
        if debug_mode: # If in debug mode, just try to run the command...
            Routing.route_command(data['text'], data, client)
        else: # otherwise, run it with error detection.
            try:
                Routing.route_command(data['text'], data, client)
            except Exception as e:
                print(f"{utils.Colors.White}{utils.Colors.Red}[Error] {utils.Colors.White}{e.__class__.__name__}: {utils.Colors.Blue}{e}{utils.Colors.White}")

client.onAnyMessage(handle_new_message) # When a message is received, process it using the above function.
client.sendText(MyNumber, "Brian Initialised") # Let the owner know the bot is running.
client.io.wait() # Wait for the next message to prevent the script from just stopping.
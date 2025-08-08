import BOT.utils as utils, BOT.Routing as Routing, BOT.DbMgmt as DbMgmt, datetime, time, threading, BOT.exeQueue as exeQueue, BOT.globals as globals
from WPP_Whatsapp import Create
# brian\scripts\activate

Admins = globals.Admins

creator = Create(session="brianv2", browser='chrome', headless=True, catchQR=utils.catchQR, logQR=True, qr='terminal')
client = creator.start()

import threading
import sys
import os

HEALTH_CHECK_INTERVAL = 10  # seconds
MAX_FAILED_PINGS = 3
failed_pings = 0

def health_check_loop():
    global failed_pings
    while True:
        try:
            # Replace with a lightweight, always-safe API call
            client.getHostDevice()  # or any harmless method
            failed_pings = 0  # Reset on success
        except Exception as e:
            failed_pings += 1
            print(f"[WA-HEALTH] Health check failed ({failed_pings}/{MAX_FAILED_PINGS}): {e}")
            if failed_pings >= MAX_FAILED_PINGS:
                print("[WA-HEALTH] Max failed health checks reached. Restarting chatbot...")
                os.execv(sys.executable, [sys.executable] + sys.argv)
        time.sleep(HEALTH_CHECK_INTERVAL)

# Start the health check thread
t = threading.Thread(target=health_check_loop, daemon=True)
t.start()

def log_and_notify_admin(msg):
    print(f"[WA-CONN] {msg}")
    try:
        client.sendText(Admins[0], f"[WA-CONN] {msg}")
    except Exception as e:
        print(f"[WA-CONN] Could not notify admin: {e}")

def handle_state_change(state):
    log_and_notify_admin(f"Connection state changed: {state}")
    if state == 'DISCONNECTED':
        log_and_notify_admin("WhatsApp client disconnected. Attempting to reconnect...")
        try:
            creator.reconnect()
            log_and_notify_admin("Reconnection attempt finished.")
        except Exception as e:
            log_and_notify_admin(f"Reconnection failed: {e}")
            sys.exit(1)
    elif state == 'QR_REQUIRED':
        log_and_notify_admin("QR code required. Please scan to continue.")
    elif state == 'CONNECTED':
        log_and_notify_admin("WhatsApp client connected.")
    elif state == 'ERROR':
        log_and_notify_admin("WhatsApp client error. Exiting.")
        sys.exit(1)

client.onStateChange(handle_state_change)

if creator.state != 'CONNECTED':
    log_and_notify_admin(f"Initial state: {creator.state}")
    raise Exception(creator.state)

def handle_new_message(msg):
    """Function to handle new messages received by the client."""
    global client
    
    if str(msg.get("chatId").get("_serialized")) != "status@broadcast" and msg.get("body"): # checking that the message is valid and not a status message
        # Get the data into a more useable dict.
        data = utils.newGetMessageData(msg)

        # Save the message to the database (if the database is already in use, it retries up to 10 times with a backoff).
        try:
            DbMgmt.saveRecord(data['chatId'], datetime.datetime.now(datetime.UTC).timestamp(), data['text'], data['authorId'], data['messageId'])
        except:
            for i in range(4):
                try:
                    DbMgmt.saveRecord(data['chatId'], datetime.datetime.now(datetime.UTC).timestamp(), data['text'], data['authorId'], data['messageId'])
                    break
                except: time.sleep(i)

        # Print the message using the correct format, depending on user status and other variables
        utils.printMessage(data['text'], data['authorId'], data['authorName'])

        chat = data["chatId"]

        skipCheck = str(data['authorId']) in Admins # If it's the admin, skip the whitelist check.
        
        # If the message is a suspected comand...
        if data["text"][0] == "!":
            try:
                Routing.route_command(data['text'], chat, skipCheck, data, client)
            except Exception as e:
                print(f"{utils.Colors.White}{utils.Colors.Red}[Error] {utils.Colors.White}{e.__class__.__name__}: {utils.Colors.Blue}{e}{utils.Colors.White}")

executor = threading.Thread(target=exeQueue.jobProcessor).start()

print("Initialised the client successfully!")

client.sendText(Admins[0], "Brian (v2) started successfully!")

# Add Listen To New Message

creator.client.onAnyMessage(handle_new_message)

globals.main_loop = creator.loop
globals.client = client

creator.loop.run_forever()
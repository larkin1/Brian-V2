import datetime
import time
import threading
import sys
import os
import shutil
from pathlib import Path

from WPP_Whatsapp import Create

import BOT.utils as utils
import BOT.Routing as Routing
import BOT.DbMgmt as DbMgmt
import BOT.exeQueue as exeQueue
import BOT.globals as globals
import BOT.session as session

Admins = globals.Admins

creator = Create(
    session="brianv2", 
    browser='chrome', 
    headless=True, 
    catchQR=utils.catchQR, 
    logQR=True, 
    qr='terminal'
)

client = creator.start()

HEALTH_CHECK_INTERVAL = 10 # seconds
MAX_FAILED_PINGS = 2
failed_pings = 0

target = Path("TEMP")
if target.exists():
    shutil.rmtree(target)

def health_check_loop():
    """
    Make sure the browser session isn't borked.
    Restarts the bot if it is.
    There is prolly a better way than just restarting the whole bot but ehh.
    """
    global failed_pings
    
    while True:
        
        try:
            client.getHostDevice()  # Harmless Method to check browser state
            failed_pings = 0  # Reset on success
            
        except Exception as e:
            failed_pings += 1
            
            message = (
                f"{utils.Colors.Red}[ERROR] "
                f"{utils.Colors.White}HealthCheck: "
                f"{utils.Colors.Blue}Fault ({failed_pings}/{MAX_FAILED_PINGS}): {e}"
            )
            print(message)
            
            if failed_pings >= MAX_FAILED_PINGS:
                
                message = (
                    f"{utils.Colors.Red}[ERROR] "
                    f"{utils.Colors.White}HealthCheck: "
                    f"{utils.Colors.Blue}Max checks reached..."
                    f"{utils.Colors.White}\nRestarting..."
                )
                print(message)
                                
                os.execv(sys.executable, [sys.executable] + sys.argv)
                
        time.sleep(HEALTH_CHECK_INTERVAL)


def log_and_notify_admin(msg):
    """
    Logs a message and sends it to the admin.
    """
    message = (
        f"{utils.Colors.Red}[Error] "
        f"{utils.Colors.White}StateHandler: "
        f"{utils.Colors.Blue}{msg}"
    )
    print(message)
    
    # I got sick of constant messages, thus the commented out section.
    # try:
    #     client.sendText(Admins[0], f"[WA-CONN] {msg}")
    # except Exception as e:
    #     print(f"[WA-CONN] Could not notify admin: {e}")


def handle_state_change(state):
    """
    Identify what happened, and log it.
    """
    log_and_notify_admin(f"Connection state changed: {state}")
    if state == 'DISCONNECTED':
        log_and_notify_admin(
            "WhatsApp client disconnected. Attempting to reconnect..."
        )
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

def database_save(data):
    try:
        DbMgmt.saveRecord(
            data['chatId'], 
            datetime.datetime.now(datetime.UTC).timestamp(), 
            data['text'], 
            data['authorId'], 
            data['messageId']
        )
    except: # if the db is in use, retry with backoff
        for i in range(4): 
            try:
                DbMgmt.saveRecord(
                    data['chatId'], 
                    datetime.datetime.now(datetime.UTC).timestamp(), 
                    data['text'], 
                    data['authorId'], 
                    data['messageId']
                )
                break
            except: time.sleep(i)


def handle_new_message(msg):
    """Function to handle new messages received by the client."""
    global client
    
    if (
        str(msg.get("chatId").get("_serialized"))
        != "status@broadcast" 
        and msg.get("body")
    ): # checking that the message is valid and not a status message

        # Get the data into a more useable dict.
        data = utils.newGetMessageData(msg)

        # Echo loop Check for sessions.
        try:
            if session.should_suppress(data['chatId'], data['text']):
                return
        except Exception:
            pass

        # Save the message to the database
        threading.Thread(
            target=database_save, 
            args=(data,)
        ).start()

        # Print the message in ~fancy~
        utils.printMessage(
            data['text'], 
            data['authorId'], 
            data['authorName']
        )

        chat = data["chatId"]

        # If it's the admin, skip the whitelist check.
        skipCheck = str(data['authorId']) in Admins
        
        # If the message is a suspected command, route it. 
        # Otherwise, if a stream is active, forward to its handler.
        if data["text"][0] == "!":
            try:
                Routing.route_command(
                    data['text'], 
                    chat, 
                    skipCheck, 
                    data, 
                    client
                )
            except Exception as e:
                error_message = (
                    f"{utils.Colors.Red}[Error] "
                    f"{utils.Colors.White}{e.__class__.__name__}: "
                    f"{utils.Colors.Blue}{e}{utils.Colors.White}"
                )
                print(error_message)
        else:
            try:
                if session.is_active(chat):
                    handler = session.get_handler(chat)
                    if handler:
                        handler(data, client)
            except Exception as e:
                error_message = (
                    f"{utils.Colors.Red}[Stream Error] "
                    f"{utils.Colors.White}{e.__class__.__name__}: "
                    f"{utils.Colors.Blue}{e}{utils.Colors.White}"
                )
                print(error_message)

if __name__ == "__main__":
    threading.Thread(
        target=health_check_loop, 
        daemon=True
    ).start()

    client.onStateChange(handle_state_change)

    if creator.state != 'CONNECTED':
        log_and_notify_admin(f"Initial state: {creator.state}")
        raise Exception(creator.state)

    executor = threading.Thread(target=exeQueue.jobProcessor).start()

    print("Initialised the client successfully!")

    try:
        client.sendText(Admins[0], "Brian started successfully!")
    except:
        pass
    # Add Listen To New Message

    creator.client.onAnyMessage(handle_new_message)

    globals.main_loop = creator.loop
    globals.client = client

    creator.loop.run_forever()

debug_mode = input("Start in Debug mode? (y/n): ")
if debug_mode.lower().strip() == "y":
    debug_mode = True
else: 
    debug_mode = False

from wa_automate_socket_client import SocketClient
import utils, Routing, DbMgmt, datetime

if __name__ == "__main__":
    MyNumber = 'REDACTED@c.us'
    client = SocketClient('http://localhost:8085/', 'secure_api_key')

    messageList = {}

    def handle_new_message(msg):
        data = utils.getMessageData(msg)

        DbMgmt.saveRecord(data['chatId'], datetime.datetime.now(datetime.UTC).timestamp(), data['text'], data['authorId'])

        utils.printMessage(data['text'], data['authorId'], data['senderName'])

        if data["text"][0] == "!":
            if debug_mode:
                Routing.route_command(data['text'], data, client)
            else:
                try:
                    Routing.route_command(data['text'], data, client)
                except Exception as e:
                    print(f"{utils.Colors.White}{utils.Colors.Red}[Error] {utils.Colors.White}{e.__class__.__name__}: {utils.Colors.Blue}{e}{utils.Colors.White}")

    client.onAnyMessage(handle_new_message)
    client.sendText(MyNumber, "Brian Initialised")
    client.io.wait()
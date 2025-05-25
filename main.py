from wa_automate_socket_client import SocketClient
import utils, Routing

if __name__ == "__main__":
    Larkin = 'REDACTED@c.us'
    client = SocketClient('http://localhost:8085/', 'secure_api_key')

    def handle_new_message(msg):
        data = utils.getMessageData(msg)

        utils.printMessage(data['text'], data['authorId'], data['senderName'])

        if data["text"][0] == "!":
            Routing.route_command(data['text'], data, client)

    client.onAnyMessage(handle_new_message)
    client.sendText(Larkin, "Brian Initialised")
    client.io.wait()


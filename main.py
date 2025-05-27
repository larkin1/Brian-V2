from wa_automate_socket_client import SocketClient
import utils, Routing

if __name__ == "__main__":
    Larkin = 'REDACTED@c.us'
    client = SocketClient('http://localhost:8085/', 'secure_api_key')

    def handle_new_message(msg):
        data = utils.getMessageData(msg)

        utils.printMessage(data['text'], data['authorId'], data['senderName'])

        if data["text"][0] == "!":
            # try:
                Routing.route_command(data['text'], data, client)
            # except Exception as e:
            #     print(f"{utils.Colors.White}{utils.Colors.Red}[Error] {utils.Colors.White}{e.__class__.__name__}: {utils.Colors.Blue}{e}{utils.Colors.White}")

    client.onAnyMessage(handle_new_message)
    client.sendText(Larkin, "Brian Initialised")
    client.io.wait()
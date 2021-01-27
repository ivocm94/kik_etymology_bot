from flask import Flask, request, Response

from kik import KikApi, Configuration
from kik.messages import messages_from_json, TextMessage

from wikt import WiktionarySearch

app = Flask(__name__)
kik = KikApi("etybot", "f893db5d-df38-4e44-ae39-8304a7b71c81")

kik.set_configuration(Configuration(webhook="https://etymologybot.herokuapp.com/incoming"))

@app.route('/incoming', methods=['POST'])
def incoming():
    if not kik.verify_signature(request.headers.get('X-Kik-Signature'), request.get_data()):
        return Response(status=403)

    messages = messages_from_json(request.json['messages'])
    
    for message in messages:
        ws = WiktionarySearch(message.body.lower())
        if (ws.existe()):
            if isinstance(message, TextMessage):
                kik.send_messages([
                    TextMessage(
                        to=message.from_user,
                        chat_id=message.chat_id,
                        body=ws.getEty()
                    )
                ])
        else:
            if isinstance(message, TextMessage):
                kik.send_messages([
                    TextMessage(
                        to=message.from_user,
                        chat_id=message.chat_id,
                        body="no"
                    )
                ])

    return Response(status=200)


if __name__ == "__main__":
    app.run(port=8000, debug=True)

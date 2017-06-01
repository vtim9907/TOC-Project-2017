import sys
from io import BytesIO

import telegram
from flask import Flask, request, send_file

from fsm import TocMachine


API_TOKEN = 'API_TOKEN'
WEBHOOK_URL = 'WEBHOOK_URL'

app = Flask(__name__)
bot = telegram.Bot(token=API_TOKEN)
machine = TocMachine(
    states=[
        'user',
        'state1',
        'state2',
        'state3',
        'state4',
        'state5',
        'state6',
        'state7',
        'state8'
    ],
    transitions=[
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'state2',
            'conditions': 'weather_query'
        },
        {
            'trigger': 'advance',
            'source': 'state2',
            'dest': 'state3',
            'conditions': 'weather_city_query'
        },
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'state4',
            'conditions': 'air_query'
        },
        {
            'trigger': 'advance',
            'source': 'state4',
            'dest': 'state5',
            'conditions': 'air_city_query'
        },
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'state6',
            'conditions': 'uv_query'
        },
        {
            'trigger': 'advance',
            'source': 'state6',
            'dest': 'state7',
            'conditions': 'uv_city_query'
        },
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'state8',
            'conditions': 'uvi_query'
        },
        {
            'trigger': 'advance',
            'source': 'user',
            'dest': 'state1',
            'conditions': 'default_query'
        },
        {
            'trigger': 'go_back',
            'source': [
                'state1',
                'state3',
                'state5',
                'state7',
                'state8'
            ],
            'dest': 'user'
        }
    ],
    initial='user',
    auto_transitions=False,
    show_conditions=True,
)


def _set_webhook():
    status = bot.set_webhook(WEBHOOK_URL)
    if not status:
        print('Webhook setup failed')
        sys.exit(1)
    else:
        print('Your webhook URL has been set to "{}"'.format(WEBHOOK_URL))


@app.route('/hook', methods=['POST'])
def webhook_handler():
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        machine.advance(update)
    return 'ok'


@app.route('/show-fsm', methods=['GET'])
def show_fsm():
    byte_io = BytesIO()
    machine.graph.draw(byte_io, prog='dot', format='png')
    byte_io.seek(0)
    return send_file(byte_io, attachment_filename='ffsm.png', mimetype='image/png')


if __name__ == "__main__":
    _set_webhook()
    app.run()

import socketio
import json 
from kafka import KafkaConsumer

sio = socketio.Client()

@sio.event
def connect():
    print('Connected to the server')

@sio.event
def custom_event(data):
    print(f'Received data: {data}')

sio.connect('http://127.0.0.1:3000')

consumer = KafkaConsumer()
consumer.subscribe(['rawTwitter'])

for msg in consumer:
    res = json.loads(msg.value.decode('utf-8')) 
    sio.emit('connection', {'data': res['text']})

import socketio
import json 
from kafka import KafkaProducer
from kafka import KafkaConsumer

sio = socketio.Client()

@sio.event
def connect():
    print('Connected to the server')

@sio.event
def custom_event(data):
    print(f'Received data: {data}')

sio.connect('http://localhost:3000')
sio.emit('custom_event', {'data': 'Start connexion'})

consumer = KafkaConsumer()
consumer.subscribe(['rawTwitter'])

for msg in consumer:
    res = json.loads(msg.value.decode('utf-8')) 
    sio.emit('custom_event', {'data': res['text']})
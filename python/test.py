import json 
import requests
from kafka import KafkaConsumer

url = "http://localhost:3000"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

consumer = KafkaConsumer()
consumer.subscribe(['rawTwitter'])

for msg in consumer:
    res = json.loads(msg.value.decode('utf-8')) 
    requests.post(url, data=msg.value, headers=headers)

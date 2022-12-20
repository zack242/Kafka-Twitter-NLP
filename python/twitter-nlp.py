import requests
import tweepy
import json 
from kafka import KafkaProducer
from kafka import KafkaConsumer

model = "cardiffnlp/twitter-roberta-base-sentiment-latest"
hf_token = "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" 

API_URL = "https://api-inference.huggingface.co/models/" + model
headers = {"Authorization": "Bearer %s" % (hf_token)}

producer = KafkaProducer(bootstrap_servers='localhost:9092')

def analysis(data):
    payload = dict(inputs=data, options=dict(wait_for_model=True))
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

consumer = KafkaConsumer()
consumer.subscribe(['rawTwitter'])

for msg in consumer:
    res = json.loads(msg.value.decode('utf-8')) 
    top_sentiment = max(analysis(res['text'])[0], key=lambda x: x['score'])
    d = dict(top_sentiment)
    print(top_sentiment)
    if d['label'] == 'positive' : 
        producer.send('positive-tweets',json.dumps(res, default=str).encode('utf-8'))
    if d['label'] == 'negative' :
        producer.send('negative-tweets',json.dumps(res, default=str).encode('utf-8'))
    if d['label'] == 'neutre' :
        producer.send('neutre-tweets',json.dumps(res, default=str).encode('utf-8'))
import tweepy
import time
import json
from kafka import KafkaProducer
import sys

rule =  sys.argv[1] + " lang:en -is:retweet"
print(rule)
bear_token = "AAAAAAAAAAAAAAAAAAAAAIZWkAEAAAAAeJD3pJ2XdPDP%2B%2FFyfd6RP%2BS9v4g%3DI3wV0t5FcqMiPjoSmpVMw9xbIWSUVtdXtVJTwwjnWnnQ787yDW"
producer = KafkaProducer(bootstrap_servers='localhost:9092')

class MyStream(tweepy.StreamingClient):
    # This function gets called when the stream is working
    def on_connect(self):
        print("Connected")

    def on_tweet(self, tweet):
        print(f"{tweet.author_id} : {tweet.public_metrics} : <<{tweet.text}>>")
        print("-"*50)
        producer.send('rawTwitter',json.dumps(dict(tweet), default=str).encode('utf-8'))
        return
    
    def reset_rules(self):
        try:
            for x in stream.get_rules().data:
                stream.delete_rules(x.id)
        except Exception as e:
            # Print the error message and handle the exception
            print(f'Error resetting rules: {e}')

stream = MyStream(bearer_token=bear_token,wait_on_rate_limit=True,daemon=True)
stream.reset_rules()
rules = [rule]
for rule in rules : 
    stream.add_rules(tweepy.StreamRule(value=rule))
    
stream.filter(expansions=["author_id"],tweet_fields=["created_at","referenced_tweets","geo","public_metrics"])


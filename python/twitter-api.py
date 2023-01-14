import tweepy
import json
from kafka import KafkaProducer
import os
import time
from dotenv import load_dotenv

load_dotenv()
bear_token = os.getenv("API_KEY_1")
producer = KafkaProducer(bootstrap_servers="localhost:9092")


class MyStream(tweepy.StreamingClient):
    # This function gets called when the stream is working
    def on_connect(self):
        print("Connected")

    def on_tweet(self, tweet):
        # print(f"{tweet.author_id} : {tweet.public_metrics} : <<{tweet.text}>>")
        # print("-" * 50)
        producer.send(
            "rawTwitter", json.dumps(dict(tweet), default=str).encode("utf-8")
        )
        time.sleep(0.5)
        return

    def reset_rules(self):
        try:
            for x in stream.get_rules().data:
                stream.delete_rules(x.id)
        except Exception as e:
            # Print the error message and handle the exception
            print(f"Error resetting rules: {e}")


stream = MyStream(bearer_token=bear_token, wait_on_rate_limit=True, daemon=True)
stream.reset_rules()

# Set the rules for filtering tweets
rules = ["music", "health", "school", "manga", "politics"]
# Add the rules to the stream
for rule in rules:
    r = rule + " lang:en -is:retweet"
    stream.add_rules(tweepy.StreamRule(value=r))

stream.filter(
    expansions=["author_id"],
    tweet_fields=["created_at", "referenced_tweets", "geo", "public_metrics"],
)

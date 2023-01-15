import tweepy
import json
from kafka import KafkaProducer
import os
import time
import nltk
from dotenv import load_dotenv
from prepocess import tweet_preprocessing

load_dotenv()
bear_token = os.getenv("API_KEY_1")
producer = KafkaProducer(bootstrap_servers="localhost:9092")


class MyStream(tweepy.StreamingClient):
    # This function gets called when the stream is working
    def on_connect(self):
        print("Connected")

    def on_tweet(self, tweet):
        sub_topics = ["politics", "manga", "health", "music", "school"]
        tweet_clean = tweet_preprocessing(tweet["text"])
        tokenized_tweet = nltk.word_tokenize(tweet_clean)
        for rule in sub_topics:
            for word in tokenized_tweet:
                if word in rule:
                    producer.send(
                        "rawTwitter",
                        json.dumps(dict(tweet), default=str).encode("utf-8"),
                    )
        time.sleep(0.25)
        return

    def reset_rules(self):
        try:
            for x in stream.get_rules().data:
                stream.delete_rules(x.id)
        except Exception as e:
            # Print the error message and handle the exception
            print(f"Error resetting rules: {e}")


stream = MyStream(bearer_token=bear_token, wait_on_rate_limit=True, daemon=True)
""""
stream.reset_rules()

# Set the rules for filtering tweets
rules = ["politics", "manga", "health", "music", "school"]
# Add the rules to the stream
for rule in rules:
    r = rule + " lang:en -is:retweet"
    print(r)
    stream.add_rules(tweepy.StreamRule(value=r))
"""
stream.filter(
    expansions=["author_id"],
    tweet_fields=["created_at", "referenced_tweets", "geo", "public_metrics"],
)

from river.feature_extraction import BagOfWords, TFIDF
from kafka import KafkaConsumer
from kafka import KafkaProducer
import json
import numpy as np
from river import ensemble
import pickle
import re
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import time

nltk.download("wordnet")

sub_topics = [["politics"], ["manga"], ["health"], ["music"], ["school"]]


def load_model(model_name):
    with open(model_name, "rb") as f:
        model = pickle.load(f)
    return model


def tweet_preprocessing(tweet):

    # This pattern will match one or more alphabetic, numeric, or underscore characters (\w+),
    # hashtags (e.g. #hello), or mentions (e.g. @hello)
    tokenizer = RegexpTokenizer(r"\w+|#\w+|@\w+")
    lemmatizer = WordNetLemmatizer()

    # tokenize then remove symbols or non-alphanumeric characters and remove stop words
    tweet_tokens = tokenizer.tokenize(tweet.lower())
    tweet_tokens = [word for word in tweet_tokens if word.isalnum()]
    tweet = " ".join(
        [word for word in tweet_tokens if word not in stopwords.words("english")]
    )

    # remove \n from the end after every sentence
    tweet = tweet.strip("\n")

    # Remove any URL
    tweet = re.sub(r"http\S+", "", tweet)
    tweet = re.sub(r"www\S+", "", tweet)

    # trim extra spaces
    tweet = " ".join(tweet.split())

    # lematize words
    tweet = lemmatizer.lemmatize(tweet)

    return tweet


def inference():
    # Set up
    consumer = KafkaConsumer()
    producer = KafkaProducer(bootstrap_servers="localhost:9092")
    consumer.subscribe(["rawTwitter"])
    model = load_model("python/modelBOW.pkl")

    for tweet in consumer:
        tweet = json.loads(tweet.value.decode("utf-8"))
        tweet_clean = tweet_preprocessing(tweet["text"])

        y_pred = model.predict_one(tweet_clean)
        time.sleep(3)
        producer.send(
            "class" + str(y_pred),
            json.dumps(tweet["text"], default=str).encode("utf8"),
        )


inference()

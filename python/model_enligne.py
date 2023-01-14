from kafka import KafkaConsumer
from kafka import KafkaProducer
import json
import pickle
import nltk
from prepocess import tweet_preprocessing

nltk.download("wordnet")

sub_topics = [["politics"], ["manga"], ["health"], ["music"], ["school"]]


def load_model(model_name):
    with open(model_name, "rb") as f:
        model = pickle.load(f)
    return model


def inference():
    # Set up
    consumer = KafkaConsumer()
    producer = KafkaProducer(bootstrap_servers="localhost:9092")
    consumer.subscribe(["rawTwitter"])
    model = load_model("python/model.pkl")

    for tweet in consumer:
        tweet = json.loads(tweet.value.decode("utf-8"))
        tweet_clean = tweet_preprocessing(tweet["text"])

        y_pred = model.predict_one(tweet_clean)
        producer.send(
            "class" + str(y_pred),
            json.dumps(tweet["text"], default=str).encode("utf8"),
        )


inference()

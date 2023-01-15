from kafka import KafkaConsumer
from kafka import KafkaProducer
import json
import pickle
import nltk
from prepocess import tweet_preprocessing
import torch
from transformers import BertModel, BertTokenizer
from river import base  # base.Transformer
from river.feature_extraction.vectorize import VectorizerMixin
import numpy as np

nltk.download("wordnet")

sub_topics = [["politics"], ["manga"], ["health"], ["music"], ["school"]]


class BertEmbeddings(base.Transformer, VectorizerMixin):
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.bert = BertModel.from_pretrained("bert-base-uncased")

    def transform_one(self, tweet_clean):  # overwriting
        tokenized_tweet = tweet_clean.split()
        embedded_tweet = []
        token_embedding = {
            token: self.bert.get_input_embeddings()(torch.tensor(id))
            for token, id in self.tokenizer.get_vocab().items()
        }
        for word in tokenized_tweet:
            # There are words for which we won't have an embedding
            if word not in token_embedding:
                pass
            else:
                embedding = token_embedding[word].detach().numpy()
                embedded_tweet.append(embedding)

        if hasattr(embedded_tweet, "__len__") and len(embedded_tweet) > 1:
            # in rare cases, the embedding is empty
            embedded_tweet_num = np.array(embedded_tweet).mean(axis=0)
        else:
            embedded_tweet_num = np.zeros(
                len(token_embedding["hello"].detach().numpy())
            )
        return dict(enumerate(embedded_tweet_num))


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

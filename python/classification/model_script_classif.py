import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import re
from river.compose import Pipeline
from river.feature_extraction import BagOfWords
from river.neighbors import KNNClassifier
from kafka import KafkaConsumer
from kafka import KafkaProducer
import json
from river import metrics
import torch
from transformers import BertModel, BertTokenizer
from river import base  # base.Transformer
from river.feature_extraction.vectorize import VectorizerMixin
import numpy as np
import pickle

nltk.download("wordnet")

# Save and load the model
def save_model(model):
    with open("modelBOW.pkl", "wb") as f:
        pickle.dump(model, f)


def load_model():
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
    return model


sub_topics = [["politics"], ["manga"], ["health"], ["music"], ["school"]]


def getLabel(tweet):
    label = -1  # DEFAULT LABEL, if the tweet gets -1, it is considered as unlabeled
    continue_ = True
    tokenized_tweet = nltk.word_tokenize(tweet)

    for i, list in enumerate(sub_topics):
        for sub_topic in list:
            for word in tokenized_tweet:
                if word in sub_topic and continue_:  # tricky
                    label = i
                    continue_ = False
    print("Final label =", label)
    return label


# Preprocess the tweets
def remove_urls(tweet):
    # Use regular expression to match URLs
    tweet = re.sub(r"https?:\/\/\S+|www\.\S+", "", tweet)
    return tweet


def tweet_preprocessing(tweet, add_stop=["covid"]):
    # print("Run tweet preprocessing -------------------")

    # Remove link
    tweet = remove_urls(tweet)

    # This pattern will match one or more alphabetic, numeric, or underscore characters (\w+),
    # hashtags (e.g. #hello), or mentions (e.g. @hello)
    tokenizer = RegexpTokenizer(r"\w+|#\w+|@\w+")
    lemmatizer = WordNetLemmatizer()
    # tokenize then remove symbols or non-alphanumeric characters and remove stop words
    tweet_tokens = tokenizer.tokenize(tweet.lower())
    tweet_tokens = [word for word in tweet_tokens if word.isalpha()]
    stop_words = set(stopwords.words("english"))
    stop_words.update(add_stop)
    tweet = " ".join([word for word in tweet_tokens if word not in stop_words])

    # remove \n from the end after every sentence
    tweet = tweet.strip("\n")

    # trim extra spaces
    tweet = " ".join(tweet.split())

    # lemmatize words
    tweet = lemmatizer.lemmatize(tweet)

    return tweet


# Get embeddings


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


producer = KafkaProducer(bootstrap_servers="localhost:9092")
# This is the function to create the batch data
def batch_data(max_sample, wait_after=10):
    print("Run Batch data function")

    # Set up the Kafka consumers
    consumer = KafkaConsumer()
    print("Trying to subscribe...")
    consumer.subscribe(["rawTwitter"])
    print("Subscribed!")

    # Initialisations
    row = 0
    unlabeled_row = 0
    acc = metrics.Accuracy()

    for tweet in consumer:

        print("Trying to read tweet...")
        tweet = json.loads(tweet.value.decode("utf-8"))
        tweet_clean = tweet_preprocessing(tweet["text"])
        print("Tweet read and cleaned!")
        # get the label of the tweet
        y = getLabel(tweet_clean)

        if y != -1:  # the labeling was successful
            print("Learning...")
            y_pred = model.predict_one(tweet_clean)
            model.learn_one(tweet_clean, y)
            acc.update(y_true=y, y_pred=y_pred)

            print("ACCURACY =", acc)
            print("Learning done!")
            row += 1

            # Send the tweet in the topic of its class
            # No sending tweets during debugging, comment these lines if you debug!
            print("Trying to send tweet...")
            producer.send(
                "tweetsClass_____" + str(y_pred),
                json.dumps(tweet_clean, default=str).encode("utf8"),
            )
            print("Tweet sent!")

        else:
            print("Unsuccessful labeling for this tweet.")
            unlabeled_row += 1

        if row % 1000 == 0:
            save_model(model)

        if row > max_sample:
            print("Batch complete!")
            break

    print("BatchData function done!")
    print("Tweets processed: ", (row + unlabeled_row))
    print(" % of labeled tweets:", row / (row + unlabeled_row))


model = Pipeline(
    ("TokenizerVectorizer", BagOfWords(lowercase=True)),
    ("Kmeans", KNNClassifier(n_neighbors=100)),
)

batch_data(50000, 10)

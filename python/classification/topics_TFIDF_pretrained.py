import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import re
from river.compose import Pipeline
from river.feature_extraction import BagOfWords, TFIDF
from river.cluster import KMeans, TextClust
from kafka import KafkaConsumer
from kafka import KafkaProducer
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import transformers

nltk.download("wordnet")
from river import ensemble
import pickle


def topic_identification(tweets, N, group_number):
    # Create a TfidfVectorizer object
    vectorizer = TfidfVectorizer(stop_words="english")

    # Fit the vectorizer to the tweets in the group
    vectorizer.fit(tweets)

    # Transform the tweets in the group into a TF-IDF matrix
    tfidf_matrix = vectorizer.transform(tweets)

    # Get the feature names (the vocabulary)
    feature_names = vectorizer.get_feature_names_out()

    # Get the top N features with the highest mean TF-IDF score
    mean_scores = tfidf_matrix.mean(axis=0)
    top_features = [
        (feature_names[i], mean_scores[0, i]) for i in mean_scores.nonzero()[1].tolist()
    ]
    top_features.sort(key=lambda x: x[1], reverse=True)
    top_features = top_features[:N]

    # Print the top features for the group
    print(f"Group {group_number + 1}:")
    for feature, score in top_features:
        print(f"{feature}: {score:.3f}")


# This function compute the TF-IDF of each class after receiving the batch data in order to infer the topics
def topics_processing(N_classes, N):

    print("Starting Topics identification/ classification")
    print("number of groups =", N_classes)
    no_groups = N_classes

    # Kafka consumer setup
    consumer_topics = KafkaConsumer(
        bootstrap_servers=["localhost:9092"], auto_offset_reset="earliest"
    )  # ,group_id=None
    # do this if its not a 'running topic'

    consumer_topics.subscribe(["tweetsClass_____" + str(i) for i in range(N_classes)])
    print("Subscribed!")
    list_of_groups = {}
    for i in range(no_groups):
        list_of_groups["list_" + str(i)] = []
    msg_no = 0

    for message in consumer_topics:
        print("Trying to read msg....")
        print("Topic msg =", message.topic)
        msg_no += 1
        print(str(msg_no) + "/50000")
        tweet = json.loads(message.value.decode("utf-8"))
        group = int(message.topic[-1])
        list_of_groups["list_" + str(group)].append(tweet)
        if msg_no == 50000:
            break

    for i, list in enumerate(list_of_groups):  # attention
        tweets = list_of_groups[list]
        print("Starting specific topic identification/ classification.")
        if len(tweets) != 0:
            topic_identification(tweets, N, i)


topics_processing(N_classes=5, N=10)

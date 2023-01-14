import json
import nltk
import numpy as np
from PIL import Image
from collections import Counter
from kafka import KafkaConsumer
from nltk.corpus import stopwords
from wordcloud import WordCloud
from prepocess import tweet_preprocessing


twitter_mask = np.array(
    Image.open(
        "/Users/zakariatozy/Library/Mobile Documents/com~apple~CloudDocs/IPP/IPP ZAK/DATAStrem/projet/python/tmp/twitter_mask.png"
    )
)
nltk.download("stopwords")

# Set up the Kafka consumer
consumer = KafkaConsumer()
consumer.subscribe(["rawTwitter"])
stop_words = stopwords.words("english")

while True:
    # Initialize the tweet and token lists
    tweets = []
    tokenized_tweets = []
    filtered_tweets = []
    all_tokens = []

    # Consume 100 messages from the Kafka topic
    for _, msg in zip(range(50), consumer):
        res = json.loads(msg.value.decode("utf-8"))
        tweets.append(res["text"])

    all_tokens = []
    for tweet in tweets:
        all_tokens.append(tweet_preprocessing(tweet))

    # Count the frequency of each token
    word_counts = Counter(all_tokens)

    # Get the N most common words
    N = 100
    top_words = [word for word, count in word_counts.most_common(N)]

    wordcloud = WordCloud(
        max_words=150,
        width=700,
        height=700,
        colormap="tab10",
        mask=twitter_mask,
        background_color="white",
        collocations=True,
    ).generate(" ".join(top_words))
    wordcloud_svg = wordcloud.to_svg(
        embed_font=True,
    )
    f = open("./python/tmp/wordcloud.svg", "w+")
    f.write(wordcloud_svg)
    f.close()

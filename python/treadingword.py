import json
import nltk
import numpy as np
from PIL import Image
from collections import Counter
from kafka import KafkaConsumer
from nltk.corpus import stopwords
from wordcloud import WordCloud
import base64
import matplotlib.pyplot as plt
import os 

twitter_mask = np.array(Image.open('/Users/zakariatozy/Library/Mobile Documents/com~apple~CloudDocs/IPP/IPP ZAK/DATAStrem/projet/twitter_mask.png'))
nltk.download('stopwords')

# Set up the Kafka consumer
consumer = KafkaConsumer()
consumer.subscribe(['rawTwitter'])
stop_words = stopwords.words('english')

while True:
    # Initialize the tweet and token lists
    tweets = []
    tokenized_tweets = []
    filtered_tweets = []
    all_tokens = []
    
    # Consume 100 messages from the Kafka topic
    for _, msg in zip(range(100), consumer):
        res = json.loads(msg.value.decode('utf-8')) 
        tweets.append(res['text'])

    # Preprocess and tokenize the tweets
    for tweet in tweets:
        # Remove unwanted characters and convert to lowercase
        tweet = tweet.lower().replace('#', '').replace('@', '').replace('http', '').replace('?','').replace('!','').replace(':','').replace(',','').replace('.','').replace("’","")
        processed_tweet = nltk.word_tokenize(tweet)
        tokenized_tweets.append(processed_tweet)

    # Remove the stopwords from the list of words
    filtered_tweets = [[word for word in tweet if word not in stop_words] for tweet in tokenized_tweets]
    
    # Flatten the list of tokens
    all_tokens = [token for tweet in filtered_tweets for token in tweet]

    # Count the frequency of each token
    word_counts = Counter(all_tokens)

    # Get the N most common words
    N = 100
    top_words = [word for word, count in word_counts.most_common(N)]

    wordcloud = WordCloud(max_words=150,colormap='tab10',mask=twitter_mask,background_color='white',collocations=True).generate(" ".join(top_words))
    
    plt.figure(figsize=(10,20), facecolor='k')
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig("/Users/zakariatozy/Library/Mobile Documents/com~apple~CloudDocs/IPP/IPP ZAK/DATAStrem/projet/python/tmp/wordcloud", facecolor='k', bbox_inches='tight')
    
   
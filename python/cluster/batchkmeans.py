import pickle
import pandas as pd
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import re
from kafka import KafkaConsumer
from kafka import KafkaProducer
import json
import time
import gensim
from nltk import word_tokenize
import numpy as np
from sklearn.cluster import MiniBatchKMeans
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import gensim.downloader as api


# Choose your embedding
#model_word2vec = gensim.models.KeyedVectors.load_word2vec_format('../Kafka-Twitter-NLP/data/word2vec_twitter_model.bin', binary=True, unicode_errors='ignore')
model_word2vec = api.load("glove-twitter-200")





# Remove the url
def remove_urls(tweet):
    # Use regular expression to match URLs
    tweet = re.sub(r'https?:\/\/\S+|www\.\S+', '', tweet)
    return tweet

# Preprocess the tweets
def tweet_preprocessing(tweet, add_stop = ['covid', "ลบ", "know", "like", "let"]):
    #print("Run tweet preprocessing -------------------")

    # Remove link
    tweet = remove_urls(tweet)

    # This pattern will match one or more alphabetic, numeric, or underscore characters (\w+),
    # hashtags (e.g. #hello), or mentions (e.g. @hello)
    tokenizer = RegexpTokenizer(r"\w+|#\w+|@\w+")
    lemmatizer = WordNetLemmatizer()
    # tokenize then remove symbols or non-alphanumeric characters and remove stop words
    tweet_tokens = tokenizer.tokenize(tweet.lower())
    tweet_tokens = [word for word in tweet_tokens if word.isalpha()]
    stop_words = set(stopwords.words('english'))
    stop_words.update(add_stop)
    tweet = " ".join(
        [word for word in tweet_tokens if word not in stop_words]
    )

    # remove \n from the end after every sentence
    tweet = tweet.strip("\n")

    # trim extra spaces
    tweet = " ".join(tweet.split())

    # lematize words
    tweet = lemmatizer.lemmatize(tweet)

    return tweet

#Get the embedding vector for a tweet
def get_emb_vect(tweet, model=model_word2vec, k=200):

    # Tokenize the tweet
    tweet_tokenize = word_tokenize(tweet)

    # Get the embedding
    embeddings = []
    # List of possible UNK 
    unk_words = []

    for token in tweet_tokenize:
        try:
            embedding = model[token]
            embeddings.append(embedding)
        except KeyError:
            # Print unknown words
            print(f"Unknow word : {token}")
            unk_words.append(token)

    # Compute the mean of the embeddings
    if len(embeddings) == 0 :
        mean_emb = np.zeros(k)
        print("Empty tweet")
    else :
        mean_emb = np.mean(embeddings, axis=0)

    return mean_emb




# Prepare the data
def prepare_data(data):
    print("Run data preparation")
    data = data[0]
    data = data.to_frame()
    data.rename(columns={0 : "tweets"}, inplace=True)
    data["tweet_clean"] = data['tweets'].apply(lambda x: tweet_preprocessing(x))
    data["embeddings"] = data["tweet_clean"].apply(lambda x: get_emb_vect(x))
    return data

# Model to train
def batchkmeans(data, k, N=5, batch_size = 100, model_path = './kmeans_file/kmeans.pkl', topic_path = './kmeans_file/topics.pickle'):
    print("Run batch kmeans model training and saving ----------------")

    # Prepare the data
    data = prepare_data(data)

    # take the column of embeddings
    X = np.vstack(data["embeddings"].values)
    
    # Train the MiniBatchKMeans model
    kmeans = MiniBatchKMeans(n_clusters= k, batch_size=batch_size, random_state=0).fit(X)

    # add a column class 
    data["class"] = kmeans.labels_

    # Compute the topics
    sub_data = data[["tweet_clean", "class"]]

    topics = topics_identification(sub_data, N)


    # Save the model to a file
    joblib.dump(kmeans, model_path)

    # Save the topics to disk
    with open(topic_path, 'wb') as handle:
        pickle.dump(topics, handle, protocol=pickle.HIGHEST_PROTOCOL)

    print("Training and saving done ----------------------")
    

# This is the function to create the batch data
def online_batch_kmeans(max_sample, model_path = './kmeans_file/kmeans.pkl', topic_path = './kmeans_file/topics.pickle'):  

    # this function has a problem when we don't have enough tweet (consumer loop gets stuck)
    print("Run Online Kmeans prediction and update data function")

    # Load the trained model from a file
    kmeans = joblib.load(model_path)

    # Load the topics from disk
    with open(topic_path, 'rb') as handle:
        topics = pickle.load(handle)

    # Set up the Kafka consumers & producers
    producer = KafkaProducer(bootstrap_servers="localhost:9092")
    consumer = KafkaConsumer()
    consumer.subscribe(
        ["rawTwitter2"]
    ) 

    # Consume the tweets 
    row = 0
    for tweet in consumer:
        tweet = json.loads(tweet.value.decode("utf-8"))
        tweet_clean = tweet_preprocessing(tweet["text"])
        embeddings = get_emb_vect(tweet_clean).reshape(1,-1)
        kmeans.partial_fit(embeddings)
        row += 1
        if row > max_sample:
            print("Batch complete")
            break
        # Send the tweet in the topic of its class
        print("Trying to send tweet...")
        producer.send(
            "tweets_Class" + str(kmeans.predict(embeddings)[0]),
            json.dumps(tweet_clean, default=str).encode("utf8"),
        )  # should we send the cleaned version?
        print("Tweet sent!")
        time.sleep(2)
    print("DOne")

# Identify the topics
def topics_identification(batch, N):

    print("Run topic Identification ---------------------")

    # Group the DataFrame by the 'class' column
    grouped_df = batch.groupby("class")

    # Create a list of miniclusters
    minibatches = [group for _, group in grouped_df]

    # Create a TfidfVectorizer object
    vectorizer = TfidfVectorizer(stop_words="english")

    # Create a list to store the top features for each group
    top_features_by_group = []

    # Fit the vectorizer to the tweets
    for group_tweets in minibatches:
        
        # Get the tweet column
        tweets = group_tweets["tweet_clean"]

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
            (feature_names[i], mean_scores[0, i])
            for i in mean_scores.nonzero()[1].tolist()
        ]
        #print(top_features)
        top_features.sort(key=lambda x: x[1], reverse=True)
        top_features = top_features[:N]

        top_features_by_group.append(top_features)

    # Print the top features for each group
    for i, group in enumerate(top_features_by_group):
        print(f"Group {i+1}:")
        for feature, score in group:
            print(f"{feature}: {score:.3f}")

    return top_features_by_group


####################################################################
# MiniBatch Kmeans (To be commentend if we want to run the online part)
#########################################################################


#data = pd.read_csv("../Kafka-Twitter-NLP/data/26k-tweet.txt", sep=";;", header=None, error_bad_lines=False)

#batchkmeans(data=data, k=4, batch_size=80, N=5)



#########################################################
# Online Kmeans
########################################################

online_batch_kmeans(1000000)
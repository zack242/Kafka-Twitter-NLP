from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import re

# Remove the url
def remove_urls(tweet):
    # Use regular expression to match URLs
    tweet = re.sub(r"https?:\/\/\S+|www\.\S+", "", tweet)
    return tweet


# Preprocess the tweets
def tweet_preprocessing(tweet, add_stop=["covid"]):
    # print("Run tweet preprocessing -------------------")

    # Remove link
    tweet = remove_urls(tweet)

    # This pattern will match one or more alphabetic, numeric,
    # or underscore characters (\w+),
    # hashtags (e.g. #hello), or mentions (e.g. @hello)
    tokenizer = RegexpTokenizer(r"\w+|#\w+|@\w+")
    lemmatizer = WordNetLemmatizer()
    # tokenize then remove symbols or non-alphanumeric characters
    # and remove stop words
    tweet_tokens = tokenizer.tokenize(tweet.lower())
    tweet_tokens = [word for word in tweet_tokens if word.isalpha()]
    stop_words = set(stopwords.words("english"))
    stop_words.update(add_stop)
    tweet = " ".join([word for word in tweet_tokens if word not in stop_words])

    # remove \n from the end after every sentence
    tweet = tweet.strip("\n")

    # trim extra spaces
    tweet = " ".join(tweet.split())

    # lematize words
    tweet = lemmatizer.lemmatize(tweet)

    return tweet

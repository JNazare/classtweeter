import sys
import tweepy
import json
import keys
from pymongo import MongoClient

twitterKeys = keys.getKeys()
CONSUMER_TOKEN=twitterKeys[0]
CONSUMER_SECRET=twitterKeys[1]
MY_ACCESS_TOKEN=twitterKeys[2]
MY_ACCESS_SECRET=twitterKeys[3]

auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
auth.set_access_token(MY_ACCESS_TOKEN, MY_ACCESS_SECRET)
api = tweepy.API(auth)

### MONGO CONNECTION ###
def connect():
    mongo_keys = keys.mongoKeys()
    connection = MongoClient(mongo_keys[0],mongo_keys[1])
    handle = connection[mongo_keys[2]]
    handle.authenticate(mongo_keys[3],mongo_keys[4])
    return handle

handle = connect()
twitter_collection = handle.collected_tweets

class CustomStreamListener(tweepy.StreamListener):
    # ...
    def on_status(self, status):
            try:
                savejson = {}
                twitter_json = status._json
                hashtag_list = []
                for hashtag in twitter_json["entities"]["hashtags"]:
                    hashtag_list.append(str(hashtag["text"]))
                savejson["text"] = str(twitter_json["text"])
                savejson["favorite_count"] = str(twitter_json["favorite_count"])
                savejson["hashtags"] = hashtag_list
                savejson["id"] = str(twitter_json["id_str"])
                savejson["user_id"]= str(twitter_json["user"]["id_str"])
                savejson["user_profile_image_url"]=str(twitter_json["user"]["profile_image_url"])
                savejson["created_at"]=str(twitter_json["created_at"])
                tweet_id = twitter_collection.insert(savejson)
            except:
                # Catch any unicode errors while printing to console
                # and just ignore them to avoid breaking application.
                pass

stream = tweepy.Stream(auth, CustomStreamListener(), timeout=None, compression=True)
stream.filter(track=['#classtweeter'])
from flask import Flask, request, session, redirect, url_for, jsonify
import flask 
from functools import wraps
import tweepy
import keys
from operator import itemgetter
from pymongo import MongoClient
from bson import json_util
from bson.json_util import dumps
from bson.json_util import loads
import json

def connect():
    mongo_keys = keys.mongoKeys()
    connection = MongoClient(mongo_keys[0],mongo_keys[1])
    handle = connection[mongo_keys[2]]
    handle.authenticate(mongo_keys[3],mongo_keys[4])
    return handle

class listener(tweepy.StreamListener):

    def __init__(self, incomingTweets=[]):
        self.incomingTweets = []

    def on_status(self, status):
        return True

    def on_data(self, data):
        return data
        # self.incomingTweets.append(data)
        # return self.incomingTweets

    def on_error(self, status):
        # print 'error'
        return False

def getAPIObject():
    auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
    token = session.get('request_token', None)
    
    auth.request_token = token

    try:
            auth.get_access_token(session['verifier'])
    except tweepy.TweepError:
            print 'Error! Failed to get access token.'
    
    #now you have access!
    api = tweepy.API(auth)
    return api

def getStreamObject():
    auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
    auth.set_access_token(MY_ACCESS_TOKEN, MY_ACCESS_SECRET)
    twitterStream = tweepy.Stream(auth, listener())
    return twitterStream

def groupnameToHashtag(name):
    return "#" + name.replace(" ", "-")

def hashtagToGroupname(hashtag):
    return hashtag.replace("-", " ")[1:]

def tweetAsUser(API, text):
    return API.update_status(status=text)

def getUserInfo(API, username):
    return API.get_user(username)

def getListofUsersInfo(API, usernames):
    allUserInfo = []
    for username in usernames:
        userInfo = getUserInfo(API, username)
        allUserInfo.append(userInfo)
    return allUserInfo

def getHashtag(twitterStream, hashtag):
    return twitterStream.filter(track=[hashtag])

def getTweetsWithAllHashtags(twitterStream, hashtags):
    concatHashtag = ' '.join(hashtags).strip()
    return concatHashtag

def sortTweets(tweets, sort_by='time'):
    if sort_by == 'time':
        return sorted(tweets, key=itemgetter('created_at')) 
    if sort_by == 'favorites':
        return sorted(tweets, key=itemgetter('favorite_count')) 
    return None

def organizeTweets(tweets):
    print type(tweets)
    organizedHashtags = {}
    for tweet in tweets:
        hashtagArray= tweet.get("hashtags", None)
        hashtagArray.sort()
        hashtagString = " ".join(hashtagArray)
        if organizedHashtags.get(hashtagString, None) != None:
            organizedHashtags[hashtagString].append(tweet)
        else:
            organizedHashtags[hashtagString] = [tweet]
    return dumps(organizedHashtags)


app = Flask(__name__)
app.secret_key = 'medialab'
    
twitterKeys = keys.getKeys()
CONSUMER_TOKEN=twitterKeys[0]
CONSUMER_SECRET=twitterKeys[1]
MY_ACCESS_TOKEN=twitterKeys[2]
MY_ACCESS_SECRET=twitterKeys[3]
CALLBACK_URL = 'http://localhost:5000/verify'
# session = dict()
 #you can save these values to a database

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("request_token", None) is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login")
def login():

    session['db'] = dict()
    auth = tweepy.OAuthHandler(CONSUMER_TOKEN, 
        CONSUMER_SECRET, 
        CALLBACK_URL)
    try: 
        #get the request tokens
        redirect_url= auth.get_authorization_url()
        session['request_token']= auth.request_token
        print session['request_token']
    except tweepy.TweepError:
        print 'Error! Failed to get request token'
    
    #this is twitter's url for authentication
    return flask.redirect(redirect_url) 

@app.route("/verify")
def get_verification():
    
    #get the verifier key from the request url
    session['verifier'] = request.args['oauth_verifier']
    api = getAPIObject()
    session['access_token']=session.get('request_token', None)

    return flask.redirect(flask.url_for('start'))

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return flask.redirect(flask.url_for('login'))

@app.route("/")
@login_required
def start():
    #auth done, app logic can begin
    api = getAPIObject()
    #example, print your latest status posts
    return flask.render_template('classtweeter.html', tweets=api.user_timeline())

@app.route('/stream')
@login_required
def stream():
    handle = connect()
    tweets = dumps(list(handle.collected_tweets.find()))
    organizedTweets = organizeTweets(loads(tweets))
    return organizedTweets

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, session, redirect, url_for, jsonify, render_template
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
import re
from datetime import datetime, timedelta
from email.utils import parsedate_tz

key_user = ''
secret_user = ''
tracked_hashtag = 'tfivefifty'

def to_datetime(datestring):
    time_tuple = parsedate_tz(datestring.strip())
    dt = datetime(*time_tuple[:6])
    return dt - timedelta(seconds=time_tuple[-1])

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


def underscore_to_camelcase(value):
    def camelcase(): 
        yield str.lower
        while True:
            yield str.capitalize

    c = camelcase()
    return "".join(c.next()(x) if x else '_' for x in value.split("_"))

def getAPIObject():
    auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
    #auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    token = session.get('request_token', None)
    auth.request_token = token
    try:
        auth.get_access_token(str(session['verifier']))
    except tweepy.TweepError:
        print 'Error! Failed to get access token.'
    
    #now you have access!
    api = tweepy.API(auth)
    global key_user
    key_user = auth.access_token
    global secret_user
    secret_user = auth.access_token_secret


    
    return api



def getStreamObject():
    auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
    auth.set_access_token(MY_ACCESS_TOKEN, MY_ACCESS_SECRET)
    twitterStream = tweepy.Stream(auth, listener())
    print ("tweet feed")
    print ('this %s' %twitterStream)
    return twitterStream

def tweetAsUser(API, text):
    print ('api %s' %API)
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
    organizedHashtags = {}
    for tweet in tweets:
        hashtagArray= tweet.get("hashtags", None)
        hashtagArray.remove(tracked_hashtag)
        hashtagArray.sort()
        hashtagString = " ".join(hashtagArray)
        tweet["created_at"] = to_datetime(tweet["created_at"]) - timedelta(hours=4)
        tweet["_id"] = str(tweet["_id"])
        for hashtag in hashtagArray:
            tweet["text"] = tweet["text"].replace("#"+hashtag, "")
        tweet["text"]=tweet["text"].replace("#"+tracked_hashtag, "")
        if "?" in tweet["text"]:
            tweet["is_question"]=True
        is_author=False
        if int(tweet["user_id"])==session["id_str"]:
            is_author=True
        if organizedHashtags.get(hashtagString, None) != None:
            organizedHashtags[hashtagString]["tweets"].append(tweet)
            organizedHashtags[hashtagString]["user_photos"].append(tweet["user_profile_image_url"])
            organizedHashtags[hashtagString]["total_favorites"]=organizedHashtags[hashtagString]["total_favorites"] + int(tweet["favorite_count"])
            if organizedHashtags[hashtagString]["is_author"] == False and is_author==True:
                organizedHashtags[hashtagString]["is_author"] = True
        else:
            organizedHashtags[hashtagString] = {"tweets": [tweet], "user_photos": 
                                                [tweet["user_profile_image_url"]], 
                                                "total_favorites": int(tweet["favorite_count"]),
                                                "is_author": is_author}
        organizedHashtags[hashtagString]["user_photos"]=list(set(organizedHashtags[hashtagString]["user_photos"]))
        organizedHashtags[hashtagString]["tweets"].sort(key=lambda x: x["created_at"], reverse=True)
        for ct in range(len(organizedHashtags[hashtagString]["tweets"])):
            organizedHashtags[hashtagString]["tweets"][ct]["created_at_str"] = datetimeformat(organizedHashtags[hashtagString]["tweets"][ct]["created_at"])
        organizedHashtags[hashtagString]["most_recent"]=organizedHashtags[hashtagString]["tweets"][0]["created_at"]
    hashtagList = []
    for hashtag in organizedHashtags:
        organizedHashtags[hashtag]["hashtagString"]=hashtag
        hashtagList.append(organizedHashtags[hashtag])
    hashtagList.sort(key=lambda x: x["most_recent"], reverse=True)
    return [dumps(hashtagList), dumps(organizedHashtags)]




def sortHashtagsinTweet(tweet):
    hashtagArray = tweet.get("hashtags", None)
    for hashtag in hashtagArray:
        tweet["text"] = tweet["text"].replace("#"+hashtag, "")
    hashtagArray.remove('classtweeter')
    hashtagArray.sort()
    hashtagString = " ".join(hashtagArray)
    return [tweet, hashtagString]

def formatDateTimeofTweet(tweet):
    tweet["created_at"] = to_datetime(tweet["created_at"]) - timedelta(hours=4)
    tweet["created_at_str"] = datetimeformat(tweet["created_at"])
    return tweet

def tagQuestioninTweet(tweet):
    tweet["is_question"]=False
    if "?" in tweet["text"]:
        tweet["is_question"]=True
    return tweet

def tagAuthorinTweet(tweet):
    tweet["is_author"]=False
    if int(tweet["user_id"])==session["id_str"]:
        tweet["is_author"]=True
    return tweet

def addTweetToDict(organizedHashtags, tweet, hashtagString):
    if organizedHashtags.get(hashtagString, None) != None:
        organizedHashtags[hashtagString]["tweets"].append(tweet)
        organizedHashtags[hashtagString]["user_photos"].append(tweet["user_profile_image_url"])
        if organizedHashtags[hashtagString]["is_author"] == False and tweet["is_author"]==True:
            organizedHashtags[hashtagString]["is_author"] = True
    else:
        organizedHashtags[hashtagString] = {"tweets": [tweet], "user_photos": 
                                            [tweet["user_profile_image_url"]], 
                                            "total_favorites": int(tweet["favorite_count"]),
                                            "is_author": tweet["is_author"]}
    return organizedHashtags

def sortHashtagstoList(organizedHashtags):
    hashtagList = []
    for hashtag in organizedHashtags:
        hashtagList.append(organizedHashtags[hashtag])
    hashtagList.sort(key=lambda x: x["most_recent"], reverse=True)
    return hashtagList

def sortTweets(tweets):
    organizedHashtags = {}
    for tweet in tweets:
        [tweet, hashtagString] = sortHashtagsinTweet(tweet)
        tweet = formatDateTimeofTweet(tweet)
        tweet["_id"] = str(tweet["_id"])
        tweet = tagQuestioninTweet(tweet)
        tweet = tagAuthorinTweet(tweet)
        organizedHashtags = addTweetToDict(organizedHashtags, tweet, hashtagString)
    for hashtagString in organizedHashtags.keys():
        organizedHashtags[hashtagString]["user_photos"]=list(set(organizedHashtags[hashtagString]["user_photos"]))
        organizedHashtags[hashtagString]["tweets"].sort(key=lambda x: x["created_at"], reverse=True)
        organizedHashtags[hashtagString]["most_recent"]=organizedHashtags[hashtagString]["tweets"][0]["created_at"]
        organizedHashtags[hashtagString]["hashtagString"] = hashtagString
        organizedHashtags[hashtagString]["raw_data"]=json.dumps(organizedHashtags[hashtagString], default=json_util.default)
    hashtagList = sortHashtagstoList(organizedHashtags)
    return hashtagList 


app = Flask(__name__)
#static_url_path='/static'
app.secret_key = 'medialab'
    
twitterKeys = keys.getKeys()
CONSUMER_TOKEN=twitterKeys[0]
CONSUMER_SECRET=twitterKeys[1]
MY_ACCESS_TOKEN=twitterKeys[2]
MY_ACCESS_SECRET=twitterKeys[3]
#CALLBACK_URL = 'http://8d5cf986.ngrok.io/verify'
CALLBACK_URL = 'http://127.0.0.1:5000/verify'
# session = dict()
 #you can save these values to a database

def groupnameToHashtag(name):
    return "#" + name.replace(" ", "_")

@app.template_filter('hashtagToGroupname')
def hashtagToGroupname(hashtag):
    # print hashtag
    return hashtag.replace("_", " ")

@app.template_filter('strftime')
def datetimeformat(value, format='%H:%M'):
    return value.strftime(format)

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
        session['request_token']= auth.request_token ##store the request token in the session since we will need it inside the callback URL request
    except tweepy.TweepError:
        print 'Error! Failed to get request token'
    
    #this is twitter's url for authentication
    return flask.redirect(redirect_url) 

@app.route("/verify")
def get_verification():
    #get the verifier key from the request url
    session['verifier'] = request.args['oauth_verifier']
    session['oauth_token']=request.args['oauth_token']
    #api = getAPIObject()
    #session['access_token']=session.get('request_token', None)
    return flask.redirect(flask.url_for('start'))

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return flask.redirect(flask.url_for('login'))

@app.route('/stream')
@login_required
def stream(type='list'):
    handle = connect()
    tweets = dumps(list(handle.collected_tweets.find()))
    organizedTweets = organizeTweets(loads(tweets))
    if type=='list':
        return organizedTweets[0]
    if type=='dict':
        # print organizedTweets[1]
        return organizedTweets[1]

@app.route('/contentsOfHashtag', methods=['POST'])
@login_required
def contentsOfHashtag():
    hashtag = request.form["hashtag"]
    tweets = loads(stream(type='dict'))
    hashtagContents = tweets[hashtag]
    hashtagContents["groupName"]=hashtagToGroupname(hashtag).title()
    return jsonify(hashtagContents)

@app.route("/getTweetTile", methods=['POST'])
@login_required
def tweetTile():
    return render_template('tweettile.html', groups=request.json)

@app.route("/sendToTwitter", methods=['POST'])
@login_required
def sendToTwitter():
    print ("reached")
    text = request.form.to_dict().keys()[0]
    #this = getAPIObject()
    #tweetAsUser (api ,text)

    auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
    auth.set_access_token(key_user, secret_user)
    this = tweepy.API(auth)
    print ('api is %s' %this)
    print ('text %s' %text)
    print ('key_user = %s' %key_user)
    print ('secret_user = %s' %secret_user)
    
    #text = 'debug'
    #print ('api is %s' %api)
    #session["id_str"] = api.me().id
    #session['access_token']=session.get('request_token', None)
    #st = getStreamObject()
    tweetAsUser(this, text)
    #this.update_status(text)

    #return flask.render_template('classtweeter.html', groups=tweets, hashtag_to_send=hashtag_to_send)
    # return app.send_static_file('stream.js')
    # #return send_from_directory(app.app_folder, stream.js)
    return 'done'

@app.route("/")
@login_required
def start():
    print ("started")
    
    api = getAPIObject()
    print ('api == %s' %api)
    session["id_str"] = api.me().id

    #api.update_status('back again')
    tweets = dumps(list(connect().collected_tweets.find()))
    organizedTweets = sortTweets(loads(tweets))
    return flask.render_template('index.html', groups=organizedTweets, focus_group=organizedTweets[0])


@app.route('/refresh')
@login_required
def refresh():
    print ("refresh")
    handle = connect()
    tweets = dumps(list(handle.collected_tweets.find()))
    organizedTweets = sortTweets(loads(tweets))
    return render_template('tweetcard.html', groups=organizedTweets)

@app.route('/focus', methods=['POST'])
@login_required
def focus():
    return render_template('sidebar-content.html', focus_group=request.json)


@app.route("/old")
@login_required
def old():
    api = getAPIObject()
    session["id_str"] = api.me().id
    tweets = loads(stream())
    hashtag_to_send = " #" + tweets[0]["hashtagString"] + " #" + tracked_hashtag
    return flask.render_template('classtweeter.html', groups=tweets, hashtag_to_send=hashtag_to_send)


if __name__ == "__main__":
    app.debug = True
    port = 5000 #the custom port you want
    app.run(host='127.0.0.1', port=port)
    #app.run(debug=True)

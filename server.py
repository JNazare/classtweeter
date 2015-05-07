from flask import Flask, request, session, redirect, url_for, jsonify
import flask 
from functools import wraps
import tweepy
import keys
from operator import itemgetter

class listener(tweepy.StreamListener):

    def on_status(self, status):
        print 'Tweet text: ' + status.text

        for hashtag in status.entries['hashtags']:
            print hashtag['text']

        return True

    def on_data(self, data):
        print data
        return True

    def on_error(self, status):
        print status

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

app = Flask(__name__)
app.secret_key = 'medialab'
	
keys = keys.getKeys()
CONSUMER_TOKEN=keys[0]
CONSUMER_SECRET=keys[1]
MY_ACCESS_TOKEN=keys[2]
MY_ACCESS_SECRET=keys[3]
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
	print session['access_token']

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
	# print getListofUsersInfo(api, ['norders', 'zmh'])
	streamer = getStreamObject()
	# print getTweetsWithAllHashtags(streamer, ['test', 'ing', 'this'])
	# print getHashtag(streamer, 'Juliana')
	#example, print your latest status posts
	return flask.render_template('classtweeter.html', tweets=api.user_timeline())

if __name__ == "__main__":
	app.run(debug=True)

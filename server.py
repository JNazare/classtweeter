from flask import Flask, request, session, redirect, url_for
import flask 
from functools import wraps
import tweepy
import keys

app = Flask(__name__)
app.secret_key = 'medialab'

#config
	
keys = keys.getKeys()
CONSUMER_TOKEN=keys[0]
CONSUMER_SECRET=keys[1]
CALLBACK_URL = 'http://1e91c63d.ngrok.com/verify'
# session = dict()
db = dict() #you can save these values to a database

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("request_token", None) is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login")
def login():
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
	verifier= request.args['oauth_verifier']
	
	auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
	token = session.get('request_token', None)
	
	auth.request_token = token

	try:
		    auth.get_access_token(verifier)
	except tweepy.TweepError:
		    print 'Error! Failed to get access token.'
	
	#now you have access!
	api = tweepy.API(auth)

	#store in a db
	db['api']=api
	db['access_token']=session.get('request_token', None)
	print db['access_token']

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
	api = db['api']

	#example, print your latest status posts
	return flask.render_template('classtweeter.html', tweets=api.user_timeline())

if __name__ == "__main__":
	app.run(debug=True)

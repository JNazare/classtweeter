from flask import Flask
from flask import request
import flask 
import tweepy
import keys
app = Flask(__name__)

#config
	
keys = keys.getKeys()
CONSUMER_TOKEN=keys[0]
CONSUMER_SECRET=keys[1]
CALLBACK_URL = 'http://1e91c63d.ngrok.com/verify'
session = dict()
db = dict() #you can save these values to a database

@app.route("/")
def send_token():
	auth = tweepy.OAuthHandler(CONSUMER_TOKEN, 
		CONSUMER_SECRET, 
		CALLBACK_URL)
	try: 
		#get the request tokens
		redirect_url= auth.get_authorization_url()
		session['request_token']= auth.request_token
	except tweepy.TweepError:
		print 'Error! Failed to get request token'
	
	#this is twitter's url for authentication
	return flask.redirect(redirect_url)	

@app.route("/verify")
def get_verification():
	
	#get the verifier key from the request url
	verifier= request.args['oauth_verifier']
	
	auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
	token = session['request_token']
	del session['request_token']
	
	auth.request_token = token

	try:
		    auth.get_access_token(verifier)
	except tweepy.TweepError:
		    print 'Error! Failed to get access token.'
	
	#now you have access!
	api = tweepy.API(auth)

	#store in a db
	db['api']=api
	db['access_token']=auth.access_token
	db['access_token_secret']=auth.access_token_secret
	return flask.redirect(flask.url_for('start'))

@app.route("/start")
def start():
	#auth done, app logic can begin
	api = db['api']

	#example, print your latest status posts
	return flask.render_template('classtweeter.html', tweets=api.user_timeline())

if __name__ == "__main__":
	app.run(debug=True)

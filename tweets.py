import twint
import json
import requests
import pandas
import time

while True:
	c = twint.Config()
	c.Username = "brecordernews"
	c.Search = "economy OR inflation OR demand OR dollar OR business"
	c.Limit = 10
	c.Lang = "en"
	c.Store_object = True
	twint.run.Search(c)
	tweets_as_objects = twint.output.tweets_list[:1]
	tweets = tweets_as_objects[0]
	tweet_id_obj = int(tweets.id)

	print(tweet_id_obj)
	data_obj = {'tweet_id': tweet_id_obj, 'tweet': tweets.tweet}

	msg = str(data_obj['tweet'])

	jsonFile = open("muneeb.json", "r")
	data_json = json.load(jsonFile)
	json_id = int(data_json['tweet_id'])

	if json_id == int(data_obj['tweet_id']):
		print("not new")
	else :	
		with open("brecorder.json" , 'w') as file:
			json.dump(data_obj, file)
			x = requests.post("https://api.pushover.net/1/messages.json", data = {
	  "token": "adqxdzaerh9a9vzsrok9tijo8ab6sf",
	  "user": "us6vomz99kjcfwhvm33hu6eob7mwcb",
	  "message": "@Imran Khan PTI: "+msg
	})

			print("new")

	time.sleep(15)		



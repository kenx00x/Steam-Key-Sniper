import requests
import json
import steam.webauth as wa
import time
import re
import praw

def ActivateKey(keys):
	for key in keys:
		with open('PotentialKeys.txt') as myfile:
			if key in myfile.read():
				print("already tried key")
				continue
		with open('InvalidKeys.txt') as myfile:
			if key in myfile.read():
				print("already tried key")
				continue
		r = user.session.post('https://store.steampowered.com/account/ajaxregisterkey/', data={'product_key' : key, 'sessionid' : sessionID})
		blob = json.loads(r.text)

		keyfile = open("PotentialKeys.txt", "a")
		badkeyfile = open("InvalidKeys.txt", "a")
		# Success
		if blob["success"] == 1:
 	   		for item in blob["purchase_receipt_info"]["line_items"]:
  	  			print("[ Redeemed ]", item["line_item_description"])
		else:
			# Error codes from https://steamstore-a.akamaihd.net/public/javascript/registerkey.js?v=qQS85n3B1_Bi&l=english
			errorCode = blob["purchase_result_details"]
			sErrorMessage = ""
			if errorCode == 14:
				sErrorMessage = 'The product code you\'ve entered is not valid. Please double check to see if you\'ve mistyped your key. I, L, and 1 can look alike, as can V and Y, and 0 and O.'
				badkeyfile.write(key+"\n")
	
			elif errorCode == 15:
				sErrorMessage = 'The product code you\'ve entered has already been activated by a different Steam account. This code cannot be used again. Please contact the retailer or online seller where the code was purchased for assistance.'
				badkeyfile.write(key+"\n")
	
			elif errorCode == 53:
				sErrorMessage = 'There have been too many recent activation attempts from this account or Internet address. Please wait and try your product code again later.'
				keyfile.write(key+"\n")
	
			elif errorCode == 13:
				sErrorMessage = 'Sorry, but this product is not available for purchase in this country. Your product key has not been redeemed.'
				keyfile.write(key+"\n")
	
			elif errorCode == 9:
				sErrorMessage = 'This Steam account already owns the product(s) contained in this offer. To access them, visit your library in the Steam client.'
				keyfile.write(key+"\n")
	
			elif errorCode == 24:
				sErrorMessage = 'The product code you\'ve entered requires ownership of another product before activation.\n\nIf you are trying to activate an expansion pack or downloadable content, please first activate the original game, then activate this additional content.'
				keyfile.write(key+"\n")

			elif errorCode == 36:
				sErrorMessage = 'The product code you have entered requires that you first play this game on the PlayStation®3 system before it can be registered.\n\nPlease:\n\n- Start this game on your PlayStation®3 system\n\n- Link your Steam account to your PlayStation®3 Network account\n\n- Connect to Steam while playing this game on the PlayStation®3 system\n\n- Register this product code through Steam.'
				keyfile.write(key+"\n")

			elif errorCode == 50: 
				sErrorMessage = 'The code you have entered is from a Steam Gift Card or Steam Wallet Code. Browse here: https://store.steampowered.com/account/redeemwalletcode to redeem it.'
				keyfile.write(key+"\n")
	
			else:
				sErrorMessage = 'An unexpected error has occurred.  Your product code has not been redeemed.  Please wait 30 minutes and try redeeming the code again.  If the problem persists, please contact <a href="https://help.steampowered.com/en/wizard/HelpWithCDKey">Steam Support</a> for further assistance.'
				keyfile.write(key+"\n")

			print("[ Error ]", sErrorMessage)

def CheckNew():
	time.sleep(1) #Reddit api has 1 second request buffer :V
	r = praw.Reddit(user_agent = "Steam Key Scraper")
	subreddit = r.subreddit('pcgaming+gaming+steam_giveaway+pcmasterrace+FreeGameFindings+FreeGamesOnSteam+GiftofGames+FREE+humblebundles+Steam_Keys+FreeSteamKeys+Free_steam_keys')
	stream = praw.models.util.stream_generator(lambda **kwargs: submissions_and_comments(subreddit, **kwargs))

	for post in stream:
		try:
			submission = post.selftext
		except:
			submission = post.body
		m = re.findall('[a-zA-Z0-9]{5}\-[a-zA-Z0-9]{5}\-[a-zA-Z0-9]{5}', re.sub('[^A-Za-z0-9-]+', '', submission))
		ActivateKey(list(filter(None, m)))
		fullstring = str(m)+" - "+ str(submission)+" - " + str(post.subreddit)
		print(fullstring)

def submissions_and_comments(subreddit, **kwargs):
	results = []
	results.extend(subreddit.new(**kwargs))
	results.extend(subreddit.comments(**kwargs))
	results.sort(key=lambda post: post.created_utc, reverse=True)
	return results

print("give username")
username = input()
print("give password")
password = input()
user = wa.WebAuth(username,password)
try:
	user.login()
except wa.EmailCodeRequired:
	print("give email code")
	code = input()
	user.login(email_code=code)
except wa.TwoFactorCodeRequired:
	print("give 2FA code")
	code = input()
	user.login(twofactor_code=code)
sessionID = user.session.cookies.get_dict()["sessionid"]
		
while True:
	CheckNew()
	time.sleep(60)
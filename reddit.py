import praw
import pandas as pd
import datetime as dt
from ftplib import FTP
import random as r
import passwords
from wallstreet import Call, Put
import json 
import datetime as dt

#TO DO
#	Add a trading system 
#	Make sure that the posts are new (last 24 hours)
#	Set it up so that it runs once-a-day everyday at noon

#these tickers are problematic as they often come up in daily speech
#sorry Dave and Busters (play) and Atlassian (team) 
tickersToSkip = ["on", "has", "good", "play", "next", "turn", "any", "east", "self", "form", "stay", "beat", "car", "glad", "care", "else", "tell", "old", "road", "cash", "live", "baby", "run", "grow", "auto", "meet", "ever", "info", "mind", "fold", "wash", "chef", "lazy", "z", "roll", "fast", "alot", "team", "five", "laws", "cost", "jobs", "true", "love", "gain", "life"]

#will return a json object with portoflio information
def getCurrentPortfolio():
	jsonFile = open("data.txt")
	ret = json.load(jsonFile)
	jsonFile.close()
	return ret

#given some json will save to the file
def savePortfolio(jsonPortfolio):
	jsonFile = open("data.txt", "w")
	json.dump(jsonPortfolio, jsonFile)
	jsonFile.close()

#grabs a file that has all of the ticker symbols
def getTickerFile():
	ftp = FTP('ftp.nasdaqtrader.com')
	ftp.login()       
	ftp.cwd("/symboldirectory")
	filename = 'nasdaqlisted.txt'
	localfile = open(filename, 'r')
	ftp.quit()
	return localfile


#binary search implementation 
#true if in list, otherwise false
def quickFind(list, item):
	def quickFindHelper(list, item, start, end):
		mid = int((end+start)/2)
		if (item < list[mid]):#go left
			if (start >= end):
				return False
			return quickFindHelper(list, item, start, mid-1)
		elif (item > list[mid]):#go right
			if (start >= end):
				return False
			return quickFindHelper(list, item, mid+1, end)
		else:
			return True
	return quickFindHelper(list, item, 0, len(list)-1)

#returns a boolean 
#checks if a list is sorted
def isSorted(list):
	for i in range(len(list)-1):
		if (list[i] > list[i+1]):
			return False
	return True

#takes the special ticker file and turns it into a list of tickers
#the list will be all lowercase
#will remove problematic tickers
def fileToList(file):
	ret = []
	for line in file.readlines()[1:-1]:
		parts = line.split("|")
		tick = parts[0].lower()
		if not tick in tickersToSkip:
			ret.append(parts[0].lower())	
	return ret

#makes sure that list is sorted correctly
#good to check considering the list being pulled from the internet
def test(myList, numberOfRandoms):
	ret = True

	#make sure list is sorted
	test = isSorted(myList)
	ret &= test
	if (not test):
		print("LIST IS SORTED " + str(test))
	
	#make sure list is not empty
	test = len(myList)!= 0
	ret &= test
	if (not test):
		print("LIST IS FULL " + str(test))

	#make sure binary search works
	for i in range(numberOfRandoms):
		test = quickFind(myList, myList[r.randint(0,len(myList)-1)])
		ret &= test
		if (not test):
			print("BINARY SEARCH " + str(test))

	test = quickFind(myList, myList[0])
	ret &= test
	if (not test):
		print("BINARY SEARCH 1 " + str(test))

	test = quickFind(myList, myList[-1])
	ret &= test
	if (not test):
		print("BINARY SEARCH 2 " + str(test))

	#not in list
	test = not quickFind(myList, "ABRACADBRA")
	ret &= test 
	if (not test):
		print("BINARY SEARCH 3 " + str(test))
	
	test = not quickFind(myList, "JULIAN")
	ret &= test 
	if (not test):
		print("BINARY SEARCH 4 " + str(test))
	
	test = not quickFind(myList, "MARCO")
	ret &= test 
	if (not test):	
		print("BINARY SEARCH 5 " + str(test))
	
	test = not quickFind(myList, "POLO")
	ret &= test 
	if (not test):
		print("BINARY SEARCH 6 " + str(test))
	
	test = not quickFind(myList, "ZZZZZ")
	ret &= test 
	if (not test):
		print("BINARY SEARCH 7 " + str(test))
	
	test = not quickFind(myList, "AAAAAA")
	ret &= test 
	if (not test):
		print("BINARY SEARCH 8 " + str(test))

	return ret 

#returns a list of tuples with the number of times a stock ticker is mentioned
#(tickerSymbol, # of mentions)
def findMostPopularStocks(subreddit, tickerList):
	values = {}
	for submission in subreddit.new(limit=100):
		submission.comments.replace_more(limit=0)
		all_comments = submission.comments.list()
		for comment in all_comments:
			searchableComment = comment.body.lower()
			for tick in tickerList:
				if tick in searchableComment:
					if values.get(tick) != None:
						values[tick] = values.get(tick)+1
					else:	
						values[tick] = 1
	return sorted(values.items(), key = lambda x: x[1], reverse = True)

#returns a list of tuples with the reactions to each symbols
#(tickerSymbol, + (is a buy) / - (is a sell))
def stockReactions(subreddit, tickerList):
	positiveWords = ["buy", "long", "calls"]
	negativeWords = ["sell", "short", "puts"]
	values = {}
	for submission in subreddit.new(limit=100):
		submission.comments.replace_more(limit=0)
		all_comments = submission.comments.list()
		for comment in all_comments:
			searchableComment = comment.body.lower().split(" ")
			print(searchableComment)
			for tick in tickerList:
				if tick in searchableComment:
					for pWord in positiveWords:
						if pWord in searchableComment:
							if values.get(tick) != None:
								values[tick] = values.get(tick)+1
							else:	
								values[tick] = 1
							break
					for nWord in negativeWords:
						if nWord in searchableComment:
							if values.get(tick) != None:
								values[tick] = values.get(tick)-1
							else:	
								values[tick] = -1
							break
	return sorted(values.items(), key = lambda x: x[1], reverse=True)

#given a string containing a date (formatted via wallstreet)
#returns a date time version 
def convertDate(dateString):
	return 0

#given a ticker will find an option (ideally with a 3 month expiry date)
def getOption(tickerSymbol):
	return 0

#given the list will update the portfolio accordingly 
#including writng to the file
def updatePortfolio(reactionList):
	return 0

#uses all of the other functions
def run():
	tickerFile = getTickerFile()
	tickerList = fileToList(tickerFile)
	if (not test(tickerList, 100)):
		print("Failed testing")
		return
	else:
		print("Test Passed")

	reddit = praw.Reddit(client_id= passwords.clientID, \
						client_secret= passwords.clientSecret,\
						user_agent=passwords.agent)

	subreddit = reddit.subreddit('wallstreetbets')

	print(stockReactions(subreddit, tickerList))
	print(searchableComment,"**" ,tick)

run()

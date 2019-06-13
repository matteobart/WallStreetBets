from wallstreet import Call, Put, Stock
import datetime as dt
import random as r
from fileManager import *
# 	*********************
#	*	REDDIT FUNCS	*
# 	*********************

#returns a list of tuples with the number of times a stock ticker is mentioned
#(tickerSymbol, # of mentions)
#NOTE: func is not used, but interested to see results (also can be used for debugging)
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
			searchableComment = comment.body.lower().replace("\n", " ").split(" ")
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


# 	*********************
#	*	 STOCK FUNCS	*
# 	*********************


#given a ticker symbol
#will return price
def getStockPrice(tickerSymbol):
	s = Stock(tickerSymbol, source="yahoo")
	return s.price


#given a ticker will find an option (ideally with a 3 month expiry date)
def getOption(tickerSymbol, isCall):
	price = getStockPrice(tickerSymbol)
	date = getFutureDate()
	opt = None
	try: 
		opt = Call(tickerSymbol, d=date[0], m=date[1], y=date[2], source="yahoo") if isCall else Put(tickerSymbol, d=date[0], m=date[1], y=date[2], source="yahoo")
	except:
		print("No options avail")
	return opt



# 	*********************
#	*	  DATE FUNCS	*
# 	*********************

#given a string containing a date (formatted via wallstreet)
#dd-mm-yyyy
#returns a date time object 
def convertDate(dateString):
	return dt.datetime.strptime(dateString, '%d-%m-%Y')

#given a date time object, will convert to a tuple
#Format: (day, month, year)
def dateToTuple(date):
	return (date.day, date.month, date.year)


#this returns date as a tuple
#this returns a date 3 months in the future
#Format: (day, month, year)
def getFutureDate():
	currentDate = dt.datetime.now() + dt.timedelta(days=90)
	return (currentDate.day, currentDate.month, currentDate.year)


# 	*********************
#	*	GENERAL FUNCS	*
# 	*********************

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

# 	*********************
#	*	PORTFOLIO FUNCS	*
# 	*********************


#given the list will return the values to update your portfolio  
#will return a tuple 
#Tuple Format: (spent, newOptions)
#NewOptions Format: 
#	[{'Stock Name': 'AMD', 'Underlying Price': 26.44, 'Price': 2.26, 'Strike': 24, 'Expiry': '19-07-2019', 'Call': True},...]
def newPortfolio(reactionList, currentPortfolio):
	print(reactionList)
	optionsToBuy = []
	if (len(reactionList)>5):
		for i in range(-3, 3):
			toAdd = getOption(reactionList[i][0], True if i >= 0 else False)
			if toAdd != None:
				optionsToBuy.append(toAdd)
	for option in optionsToBuy:
		#lets find the best strike price to use
		bestStrike = option.strikes[0]
		price = option.underlying.price
		for strike in option.strikes:
			if abs(bestStrike-price) > abs(strike-price):
				bestStrike = strike
		option.set_strike(bestStrike)
		add = {}
		add["Stock Name"] = option.ticker
		add["Underlying Price"] = option.underlying.price
		add["Strike"] = bestStrike
		add["Price"] = option.price
		add["Expiry"] = option.expiration
		add["Call"] = not isinstance(option, Put) #using isinstance(option, Call) always return True
		oldSpent = currentPortfolio["Spent"]
		newSpent = oldSpent + option.price * 100
		oldValue = currentPortfolio["Value"]
		newValue = oldValue + option.price * 100
		newLog(option.ticker, option.expiration, bestStrike, option.price, oldValue, newValue, oldSpent, newSpent) #still need to be filled in
		currentPortfolio["Spent"] = newSpent
		currentPortfolio["Value"] = newValue
		currentPortfolio["Current Options"].append(add)
	return currentPortfolio

#given a portfolio (in json) will return the updated value
#does not actually change the files
def updatePortfolio(currentPortfolio):
	value = currentPortfolio["Value"]
	for i in reversed(range(len(currentPortfolio["Current Options"]))):
		optionInfo = currentPortfolio["Current Options"][i]
		date = convertDate(optionInfo["Expiry"])
		dateTup = dateToTuple(date)
		#update the Price, Underlying Price, and add it to value
		name = optionInfo["Stock Name"]
		strike = optionInfo["Strike"]
		isCall = optionInfo["Call"]
		option = Call(name, d=dateTup[0], m=dateTup[1], y=dateTup[2], strike=strike, source="yahoo") if isCall else Put(name, d=dateTup[0], m=dateTup[1], y=dateTup[2], strike=strike, source="yahoo")
		#lets update
		oldValue = value
		value += (option.price - optionInfo["Price"]) * 100
		refreshLog(name, date, strike, optionInfo["Price"], option.price, oldValue, value, currentPortfolio["Spent"])
		optionInfo["Price"] = option.price
		optionInfo["Underlying Price"] = option.underlying.price
		#if option is expired, lets move it
		if (date <= dt.datetime.now()):
			currentPortfolio["Past Options"].append(optionInfo)
			del currentPortfolio["Current Options"][i]
	#reset the new value for the portfolio
	currentPortfolio["Value"] = value
	return currentPortfolio



# 	*********************
#	*	TESTING FUNCS	*
# 	*********************


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

import datetime as dt
from ftplib import FTP
import json 


#any function that has to do with files (open, closing, writing, etc) will be here

dataFilename = "data.txt"
logfile = open("log.txt", "a")


#these tickers are problematic as they often come up in daily speech
#sorry Dave and Busters (play) and Atlassian (team) 
tickersToSkip = ["on", "has", "good", "play", "next", "turn", "any", "east", "self", "form", "stay", "beat", "car", "glad", "care", "else", "tell", "old", "road", "cash", "live", "baby", "run", "grow", "auto", "meet", "ever", "info", "mind", "fold", "wash", "chef", "lazy", "z", "roll", "fast", "alot", "team", "five", "laws", "cost", "jobs", "true", "love", "gain", "life", "once", "tech", "core", "nice", "blue", "hope", "act", "fund", "rare", "calm", "eye", "fat", "jack", "type", "hope"]


def newLog(tick, expiry, strike, price, oldValue, newValue, oldSpent, newSpent):
	logfile.write(f"{dt.datetime.now()} | Added {tick} Exp: {expiry} Strike: {strike} Cost: {price}\n")
	logfile.write(f"\tPortfolio Value: {oldValue} -> {newValue} | Spent: {oldSpent}->{newSpent}\n\n")

def refreshLog(tick, expiry, strike, oldPrice, newPrice, oldValue, newValue, spent):
	logfile.write(f"{dt.datetime.now()} | Updated {tick} Exp: {expiry} Strike: {strike}\n")
	logfile.write(f"\tPrice: {oldPrice} -> {newPrice}| Portfolio Value: {oldValue} -> {newValue} | Spent: {spent}\n\n")

#will return a json object with portoflio information
def getCurrentPortfolio():
	try:
		jsonFile = open(dataFilename)
		ret = json.load(jsonFile)
		jsonFile.close()
	except: 
		ret = {"Spent": 0, "Value": 0, "Past Options": [], "Current Options": []}
	return ret

#given some json will save to the file
def savePortfolio(jsonPortfolio):
	jsonFile = open(dataFilename, "w")
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


#takes the special ticker file and turns it into a list of tickers
#the list will be all lowercase
#will remove problematic tickers
def nasdaqTickerToList(file):
	ret = []
	for line in file.readlines()[1:-1]:
		parts = line.split("|")
		tick = parts[0].lower()
		if not tick in tickersToSkip:
			ret.append(parts[0].lower())	
	return ret

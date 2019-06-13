import praw
import passwords
from helpers import *
from fileManager import *

#TO DO
#	Make sure that the posts are new (last 24 hours)
#	Set it up so that it runs once-a-day everyday at noon
#	Make sure that the least popular stocks are actually negative
#	Solved: Make sure that the options will work (new stocks won't have options)


#NOTES
#	It is possible that less than 6 stocks are added
#		If reactionList is too small
#		If no options are avail will simply skip it (no replacement)



#uses all of the other functions
def run():
	tickerFile = getTickerFile()
	tickerList = nasdaqTickerToList(tickerFile)
	if (not test(tickerList, 100)):
		print("Failed testing")
		return
	else:
		print("Test Passed")

	reddit = praw.Reddit(client_id= passwords.clientID, \
						client_secret= passwords.clientSecret,\
						user_agent=passwords.agent)

	subreddit = reddit.subreddit('wallstreetbets')
	reactions = stockReactions(subreddit, tickerList)
	currentPortfolio = getCurrentPortfolio()
	currentPortfolio = updatePortfolio(currentPortfolio)
	currentPortfolio = newPortfolio(reactions, currentPortfolio)
	#time to merge toAdd and currentPortfolio
	# currentPortfolio["Spent"] += toAdd[0]
	# currentPortfolio["Value"] += toAdd[0]
	# currentPortfolio["Current Options"] += toAdd[1]
	#save it back to the file
	savePortfolio(currentPortfolio)
	logfile.close()

run()

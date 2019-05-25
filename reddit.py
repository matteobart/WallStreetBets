import praw
import pandas as pd
import datetime as dt
from ftplib import FTP
import random as r
import passwords

#grabs a file that has all of the ticker symbols
def grabFile():
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

def isSorted(list):
	for i in range(len(list)-1):
		if (list[i] > list[i+1]):
			return False
	return True

#takes the special ticker file and turns it into a list of tickers
def fileToList(file):
	ret = []
	for line in file.readlines()[1:-1]:
		parts = line.split("|")
		ret.append(parts[0])	
	return ret

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


def run():
	tickerFile = grabFile()
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

	for submission in subreddit.new(limit=100):
		#print(submission.title)
		submission.comments.replace_more(limit=0)
		all_comments = submission.comments.list()
		for comment in all_comments:
			if ("long" in comment.body.lower() or "short" in comment.body.lower()):
				print(comment.body)

run()

from datetime import datetime

# returns a 2D list of the day number in the proper slot of calendar
def generateCal(month, year):
	## Debugging statements
	#currDate = datetime.today()
	#print(currDate)
	#currMonth = currDate.month
	#print(currMonth)
	#currDay = currDate.day
	#print(currDay)

	row = [[0 for i in range(7)] for j in range(6)] 
	dayNum = 1

	# generate the week for the month
	for i in range(6):
		tempDate =  datetime(year, month, dayNum)
		dayOfWeek = remapWeekDay(tempDate.weekday())
		##print(dayOfWeek)
		# generate the day of the month
		for j in range(dayOfWeek, 7):
			##print(i, j)
			row[i][j] = dayNum
			dayNum += 1
			
			##print(checkMaxDay(month, year))
			if dayNum > checkMaxDay(month, year):
				return row

	
# will return the correct number of days in a given month and year
def checkMaxDay(month, year):
	# check for leap year
	if year % 4 == 0:
		if month == 2:
			return 29
	else:
		if month == 2:
			return 28
	
	# check months besides feb
	if month == 4 or month == 6 or month == 9 or month == 11:
		return 30
	else:
		return 31

# remap the date to 0 for sunday ... 6 for saturday
def remapWeekDay(i):
	if i == 6:
		return 0
	else:
		return i + 1
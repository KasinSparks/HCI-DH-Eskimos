from datetime import datetime

def generateCal(month, year):
	currDate = datetime.today()
	print(currDate)
	currMonth = currDate.month
	print(currMonth)
	currDay = currDate.day
	print(currDay)

	row = [[0 for i in range(7)] for j in range(6)] 
	dayNum = 1

	## generate the week for the month
	for i in range(6):
		tempDate =  datetime(year, month, dayNum)
		dayOfWeek = remapWeekDay(tempDate.weekday())
		#print(dayOfWeek)
		for j in range(dayOfWeek, 7):
			#print(i, j)
			row[i][j] = dayNum
			dayNum += 1
			
			##print(checkMaxDay(month, year))
			if dayNum > checkMaxDay(month, year):
				return row

	

def checkMaxDay(month, year):
	if year % 4 == 0:
		# leap year
		if month == 2:
			return 29
	else:
		if month == 2:
			return 28
		elif month == 4 or month == 6 or month == 9 or month == 11:
			return 30
		else:
			return 31

def remapWeekDay(i):
	if i == 6:
		return 0
	else:
		return i + 1
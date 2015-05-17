from lxml import html 
from lxml import etree
from termcolor import colored
from urllib2 import urlopen, URLError
from argparse import ArgumentParser
from bs4 import BeautifulSoup
import re
import requests
import sys

import database

##Days of the Week
##TBA = 9
##M = 0
##T = 1
##W = 2
##R = 3
##F = 4
##S = 5

##Period Conversion
## 1 = 1
## 11 = 11
## E1 = 12
## E3 = 14

SEMESTER = '201508'
BASE_URL = 'http://www.registrar.ufl.edu/soc/' + SEMESTER + '/all/'
LOCAL_URL = "C:\\Users\\Josh\\Desktop\\Schedule_Chomper_v0.0.1\\schedule_scraper"

class Meeting:
	day = ''
	start = 0
	finish = 0

class Course:
	name = ''
	course_code = ''
	section = ''
	credits = 0
	instructor = ''
	web = False
	meetings = None
	def __str__(self):
		self_string =  "Name: " + self.name + ", Code: " + self.course_code + ", Section: " + self.section \
		+ ", Credits: " + str(self.credits) + ", Instructor: " + self.instructor + ", Web: " + str(self.web) + "\n"
		for meet in self.meetings:
			self_string = self_string + "Day: " + meet.day + "[" + str(meet.start) + "," + str(meet.finish) + "]\t"
		
		return self_string
		

def get_table(page):
	# Get table
	try:
		table = page.find_all('table')[1]
	except AttributeError as e:
		print 'No tables found, exiting'
		return 1
	return table

def parse_rows(table):
	# Get rows
	##print "table length: "
	##print(len(table))
	try:
		rows = table.find_all('tr')
	except AttributeError as e:
		print 'No table rows found, exiting'
		return 1
		
	##print rows	
		
	""" Get data from rows """
	results = []
	for row in rows:
		table_headers = row.find_all('th')
		if table_headers:
			results.append([headers.get_text() for headers in table_headers])

		table_data = row.find_all('td')
		if table_data:
			results.append([data.get_text() for data in table_data])
	return results
  
def get_departments():
	page = open(LOCAL_URL + "\\" + SEMESTER + "\\accounts.htm").read()
	tree = html.fromstring(page)
	results = tree.xpath('//div/div/div/div/table/tr/td/select/option/@value')
	##popping the first useless entry. 
	results.pop(0)
	##print results
	print "Found " + str(len(results)) + " departments"
	return results
	
def create_soup_object(department):
	# Make soup
	try:
		resp = open(LOCAL_URL + "\\" + SEMESTER + "\\" + department)
	except URLError as e:
		print 'An error occured fetching %s \n %s' % (url, e.reason)   
		return 1
	soup = BeautifulSoup(resp.read())
	return soup

def clean_all_rows(rows):
	## Array Clean up
	k = 0
	while k < len(rows):
		## I only want rows with 14 columns
		if len(rows[k]) != 14:
			rows.pop(k)
		else:
			rows[k] = clean_row(rows[k])
			if rows[k][0] == '':
				rows.pop(k)
				k = k - 1
			k = k + 1
	## remove column descriptions
	rows.pop(0)	
	return rows
	
def clean_row(row):
	row.pop(11)
	row.pop(10)
	row.pop(4)
	row.pop(3)
	row.pop(2)
	row.pop(1)
	j = 0
	while j < len(row):
		row[j] = row[j].replace('\n', '').replace('\r', '')
		j = j + 1
	
	row[0] = row[0].replace(' ', '')
	row[1] = row[1].replace(' ', '')
	row[2] = row[2].replace(' ', '')
	row[3] = row[3].replace('ANGE', 'fuck')
	row[3] = row[3].replace(' ', '').replace('TBA', '9').replace('M', '0').replace('T', '1').replace('W', '2').replace('R', '3').replace('F', '4').replace('S', '5')
	if row[3] == '':
		row[3] = '9'
	if row[0] == '' and row[1] == '' and row[6] == '':
		row.pop(7)
		row.pop(6)
		row.pop(2)
		row.pop(1)
		row.pop(0)
	
	if len(row) == 3 and row[1] == 'ANGE':
		row[0] = '';
		row[1] = '';
	if len(row) == 8 and row[4] == 'ANGE':
		row[3] = '';
		row[4] = '';
	##print row
	##print '\n'
	return row
	
def organize_courses(rows):
	i = 0
	course = 0
	department = []
	while i < len(rows):
		temp = []
		##found class
		if(len(rows[i]) == 8):
			temp.append(rows[i])
			i += 1
		##looking for meetings followed by class
		while i < len(rows) and len(rows[i]) != 8:
			temp.append(rows[i])
			i += 1
		course += 1
		department.append(temp)
	return department
	
def arrange_schedule(course, t):
	i = 0
	while i < len(course):
		
		if i == 0:##Course
			days = course[i][3]
			hours = course[i][4]
		else:##Course's Extra
			days = course[i][0]
			hours = course[i][1]
		##For each day the class meets, add to Meeting() variable in the class object	
		for day in days:
			meeting = Meeting()
			meeting.day = day
			##print days
			if day != '9': ##NOT TBA COURSE
				##print hours
				##print 'E'
				##Contains Exam Courses
				if re.compile('E').search(hours) or re.compile('e').search(hours): 
					j = 0
					while j < len(hours):
						if (hours[j] == 'E' or hours[j] == 'e') and ((j - 1 > 0) and hours[j - 1] != '-'):
							##print "Hours Before", hours
							hours = hours[:j] + '-' + hours[j:]
							j += 1
							##print "Hours After", hours
						j += 1	
				##Finished adding - between E
				when = hours.split("-")

				k = 0
				while k < len(when):
					if when[k] == 'E1':
						##print '12'
						when[k] = '12'
					if when[k] == 'E2':
						##print '13'
						when[k] = '13'
					if when[k] == 'E3':
						##print '14'
						when[k] = '14'
					k += 1

				meeting.start = when[0]
				if(len(when) == 1):

					meeting.finish = int(when[0]) + 1
				else:

					meeting.finish = int(when[1]) + 1
				
			t.meetings.append(meeting)
		i += 1
	return t	
	
def process_class(course):
	
	
	t = Course()
	t.meetings = []
	t.name = course[0][6]
	t.instructor = course[0][7]
	t.course_code = course[0][0]
	t.section = course[0][1]
	if t.section == 'DEPT' or t.section == 'dept' or t.section == 'Dept':
		t.section = t.course_code + "_" + t.section + "_" + t.instructor

	##print course
	t.credits = course[0][2]
	if t.credits == "VAR":
		t.credits = 0
	
	if course[0][5] == "WEB" or course[0][5] == "Web" or course[0][5] == "web" or course[0][3] == 9:
		t.web = True
		
	t = arrange_schedule(course, t)
	

	##print colored(t, 'red')
	return t



def main():
	departments = get_departments()

	pages_to_parse = []
	k = 0
	for department in departments:
		##if k >= 10:
			##break
		pages_to_parse.append([department, create_soup_object(department)])
		k += 1

	##print "Pages: " + str(len(pages_to_parse))

	db_ready = []
	for page in pages_to_parse:
		table = get_table(page[1])
		rows = clean_all_rows(parse_rows(table))
		department = organize_courses(rows)


		for course in department:
			db_ready.append(process_class(course))


	database.remove_all_courses()

	count = 0
	for obj in db_ready:
		if count % 100 == 0:
			print count
		if database.insert_course(obj):
			count += 1

	print colored("Total Courses Inserted: ", "cyan"), count

if __name__ == '__main__':
	status = main()
	sys.exit(status)
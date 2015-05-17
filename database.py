from pymongo import MongoClient
import main
from termcolor import colored
import json

##db = courses
##collection = users
##Name: UG RES SPEECH COMM, Code: SPC4911, Section: SPC4911_DEPT_STAFF, Credits: 0, Instructor: STAFF, Web: False
##Day: 9[0,0]

connection = MongoClient('schedulechomper.com', 27017)
print connection.database_names()
courseDB = connection.courses
print courseDB
courses = courseDB.courses
print courses




##courses.insert(course)
def remove_all_courses():
	all_courses = courses.find()
	for course in all_courses:
		print colored("Removing: ", 'blue'), course
		courses.remove(course)

def print_all_courses():
	all_courses = courses.find()
	for course in all_courses:
		print course

def insert_course(class_to_insert):
	##print class_to_insert
	course = {}
	course['name'] = class_to_insert.name
	course['code'] = class_to_insert.course_code
	course['section'] = class_to_insert.section
	course['credits'] =  class_to_insert.credits
	course['instructor'] = class_to_insert.instructor
	course['web'] = class_to_insert.web
	course['time'] = []

	for meet in class_to_insert.meetings:
		course['time'].append({'day': meet.day, 'start': meet.start, 'end': meet.finish})
	#course['time'].append({'day': 4, 'start': 10, 'end': 13})
	##print course
	##print colored("Inserted: ", 'yellow'), course
	try:
		courses.insert(course)
	except:
		print colored("Failed to insert: ", 'red'), course
		return False
	return True


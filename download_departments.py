import urllib
import requests
from termcolor import colored
from lxml import html 
from lxml import etree

SEMESTER = '201508'
BASE_URL = 'http://www.registrar.ufl.edu/soc/' + SEMESTER + '/all/'

def get_departments():
	page = requests.get(BASE_URL + 'accounts.htm')
	tree = html.fromstring(page.text)
	results = tree.xpath('//div/div/div/div/table/tr/td/select/option/@value')
	##popping the first useless entry. 
	results.pop(0)
	##print results
	print "Found " + str(len(results)) + " departments"
	return results

	
def main():
	departments = get_departments()
	
	pages_to_parse = []
	k = 0
	for department in departments:
		##if k >= 1:
			##break
		testfile = urllib.URLopener()
		testfile.retrieve(BASE_URL + department, SEMESTER + "/" + department)
		print colored(department  + " Done", 'yellow')
		
if __name__ == '__main__':
	status = main()
	sys.exit(status)

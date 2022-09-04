# file for string campusgroups querying finctions


from bs4 import BeautifulSoup
import requests
import re
from dbschema import CampusGroups

CG_ALL_GROUPS_LIST_URL="https://campusgroups.rit.edu/ics_helper"

def get_all_campus_groups():
	result = requests.get(CG_ALL_GROUPS_LIST_URL)
	grouplisthtml = BeautifulSoup(result.content, 'html.parser') 

	groupsdiv = grouplisthtml.find('div', attrs={'aria-label': 'Group Calendars.'})
	groupstable = groupsdiv.find('table')
	tablerows = groupstable.find_all("tr")
	all_groups = []
	for row in tablerows:
		data = row.find_all("td")
		name = data[0].contents[0]
		identifier = data[-1].find("a")["href"]
		x = re.search("ical_club_[0-9]*\.ics", identifier) 
		identifier = int("".join(filter(str.isdigit, x[0])))
		cg = CampusGroups()
		cg.identifier = identifier
		cg.name = name
		all_groups.append(cg)
	return all_groups

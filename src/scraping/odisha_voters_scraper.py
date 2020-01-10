import requests
from bs4 import BeautifulSoup

url = 'http://election.ori.nic.in/odishaceo/findname.aspx'

data = {
    '__EVENTTARGET': '',
    '__EVENTARGUMENT': '',
    '__LASTFOCUS': '',
    '__VIEWSTATE': '/wEPDwUKLTMzNzIxNTIyOGQYAgUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgMFD3JkYlNlYXJjaEJ5TmFtZQUNcmRiU2VhcmNoQnlJRAUNcmRiU2VhcmNoQnlJRAUJR3JpZFZpZXcxDzwrAAwBCAIBZHi0RQ7FVH6j2tiXQlfE88SwM36x6rKv1tsr0B7Mk2Zi',

    '__VIEWSTATEGENERATOR': '90CC2509',
    '__EVENTVALIDATION': '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',

    'a': 'rdbSearchByName',
    'lstACNames': '1',
    'lstDistName': '0',
    'txtFName': 'a',
    'txtLName': '',
    'txtIDNo': '',
    'txtRlnFName': 'a',
    'txtRlnLName': '',
    'btnSearch': 'Search'
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': 'ASP.NET_SessionId=pr2wikgczetj2l2xnhccnmdm',
    'Host': 'election.ori.nic.in',
    'Origin': 'http://election.ori.nic.in',
    'Referer': 'http://election.ori.nic.in/odishaceo/findname.aspx',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
}

session = requests.Session()
r = session.post(url, headers=headers, data=data)

soup = BeautifulSoup(r.content, 'html.parser')
print(r.content)
tr_tags = soup.find('table', id='GridView1').find_all('tr')
for tr_tag in tr_tags:
    try:
        ac_no = tr_tag.find_all('td')[0].get_text().strip()
    except IndexError:
        continue
    part_no_name = tr_tag.find_all('td')[1].get_text().strip()
    sr_no = tr_tag.find_all('td')[2].get_text().strip()
    electoral_name = tr_tag.find_all('td')[3].get_text().strip()
    relation = tr_tag.find_all('td')[4].get_text().strip()
    age = tr_tag.find_all('td')[5].get_text().strip()
    sex = tr_tag.find_all('td')[6].get_text().strip()
    house_no = tr_tag.find_all('td')[7].get_text().strip()
    section_no_name = tr_tag.find_all('td')[8].get_text().strip()
    identity_card_number = tr_tag.find_all('td')[9].get_text().strip()
    polling_station_location = tr_tag.find_all('td')[10].get_text().strip()

    print(ac_no)
    print(part_no_name)
    print(sr_no)
    print(electoral_name)
    print(relation)
    print(age)
    print(sex)
    print(house_no)
    print(section_no_name)
    print(identity_card_number)
    print(polling_station_location)
    print('\n')
    print('*'*80)

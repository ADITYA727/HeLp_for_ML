import requests
import joblib
from bs4 import BeautifulSoup


url_first_names = 'https://www.familyeducation.com/baby-names/browse-origin/first-name/hindi?page=%s'
url_last_names = 'https://www.familyeducation.com/baby-names/browse-origin/surname/indian?page=%s'
stopwords = ['boys', 'girls', 'no results found.']

def clean_name(name):
    return name.get_text().strip().lower()


def scrape_first_names():
    boys_names = []
    girls_names = []

    for page in range(0, 10):
        r = requests.get(url_first_names % page, verify=False)
        soup = BeautifulSoup(r.content, 'html.parser')
        boys_names_selector = soup.find_all(class_='baby-names-list')[0].find_all('li')
        girls_names_selector = soup.find_all(class_='baby-names-list')[1].find_all('li')
        boys_names.extend(
            [clean_name(name) for name in boys_names_selector if clean_name(name) not in stopwords]
        )
        girls_names.extend(
            [clean_name(name) for name in girls_names_selector if clean_name(name) not in stopwords]
        )

    boys_names = list(set(boys_names))
    girls_names = list(set(girls_names))

    joblib.dump(boys_names, 'data/indian_boys_first_names.pkl')
    joblib.dump(girls_names, 'data/indian_girls_first_names.pkl')


def scrape_last_names():
    last_names = []

    for page in range(0, 6):
        r = requests.get(url_last_names % page, verify=False)
        soup = BeautifulSoup(r.content, 'html.parser')
        last_names_selector = soup.select('.baby-names-list li')
        last_names.extend(
            [clean_name(name) for name in last_names_selector if clean_name(name) not in stopwords]
        )

    last_names = list(set(last_names))
    joblib.dump(last_names, 'data/indian_last_names.pkl')


if __name__ == '__main__':
    scrape_first_names()
    scrape_last_names()

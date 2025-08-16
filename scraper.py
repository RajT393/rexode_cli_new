# Basic web scraper
import requests
from bs4 import BeautifulSoup

def scrape(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    print(soup.prettify())

if __name__ == '__main__':
    scrape('http://example.com')
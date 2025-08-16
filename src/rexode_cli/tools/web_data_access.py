import requests
from bs4 import BeautifulSoup
import os

def search_web(query):
    """Searches the web for a given query."""
    try:
        # This is a placeholder and should be replaced with a proper search API
        response = requests.get(f"https://www.google.com/search?q={query}")
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for g in soup.find_all('div', class_='g'):
            anchors = g.find_all('a')
            if anchors:
                link = anchors[0]['href']
                title = g.find('h3').text
                item = {
                    "title": title,
                    "link": link
                }
                results.append(item)
        return results
    except Exception as e:
        return f"Error searching web: {e}"

def scrape_website(url):
    """Scrapes the content of a website."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except Exception as e:
        return f"Error scraping website: {e}"

def download_file(url, save_path):
    """Downloads a file from a URL."""
    try:
        response = requests.get(url, stream=True)
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return f"Successfully downloaded file to {save_path}"
    except Exception as e:
        return f"Error downloading file: {e}"

def get_weather(location):
    """Gets the weather for a given location."""
    try:
        # This is a placeholder and should be replaced with a proper weather API
        response = requests.get(f"https://wttr.in/{location}?format=%C+%t")
        return response.text
    except Exception as e:
        return f"Error getting weather: {e}"

def get_news(topic):
    """Gets the latest news."""
    try:
        # This is a placeholder and should be replaced with a proper news API
        response = requests.get(f"https://news.google.com/search?q={topic}")
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        for article in soup.find_all('article', limit=5):
            title = article.find('h3').text
            link = article.find('a')['href']
            articles.append({"title": title, "link": f"https://news.google.com{link}"})
        return articles
    except Exception as e:
        return f"Error getting news: {e}"

def fetch_api_data(api_url):
    """Fetches data from an API."""
    try:
        response = requests.get(api_url)
        return response.json()
    except Exception as e:
        return f"Error fetching API data: {e}"

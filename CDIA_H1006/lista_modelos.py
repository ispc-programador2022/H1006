from bs4 import BeautifulSoup
import requests


def get_urls():
    website = 'https://www.autocosmos.com.ar/catalogo/vigente'
    result = requests.get(website)
    content = result.text
    soup = BeautifulSoup(content, 'lxml')

    data = []
    for box in soup.find_all('div', class_='grid-container__content m-small'):
        card = box.find_all('a', class_='multi-link-card__header')
        for uri in card:
            data.append(uri['href'])

    return data

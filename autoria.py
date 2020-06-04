import requests, csv
from bs4 import BeautifulSoup

HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/81.0.4044.122 Chrome/81.0.4044.122 Safari/537.36',
           'accept': '*/*'}
HOST = 'https://auto.ria.com'
FILE = 'al_cars.csv'


def get_html(url,params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('span', class_='mhide')
    if pagination:
        return int(pagination[-1].get_text())
    else:
        return 1


def content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='proposition')
    cars = []
    for item in items:
        try:
            price = item.find('span', class_='grey size13').get_text(strip=True)
        except:
            price = "Not Available"
        cars.append({
            'title': item.find('h3', class_='proposition_name').get_text(strip=True),
            'price_usd': item.find('div', class_='proposition_price').find('span').get_text(strip=True),
            'price_ukr': price,
            'city': item.find('svg', class_='svg svg-i16_pin').find_next('strong').get_text(strip=True),
            'link': HOST + item.find('h3', class_='proposition_name').find('a').get('href'),
            'title_lower': item.find('div', class_='proposition_equip size13 mt-5').get_text(strip=True)
        })
    return cars


def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Марка', 'Price USD', 'Gryvnya', 'City', 'Link', 'Low Title'])
        for item in items:
            writer.writerow([item['title'], item['price_usd'], item['price_ukr'], item['city'],
                             item['link'], item['title_lower']])


def all_cars_links():
    html = get_html('https://auto.ria.com/newauto/catalog/')
    soup = BeautifulSoup(html.text, 'html.parser')
    pagination = soup.find_all('a', class_='item-brands')
    cars_list = []
    for car in pagination:
        carr = car.get('href').replace('catalog/', 'marka-')
        cars_list.append('https://auto.ria.com'+carr)
    print(len(cars_list))
    return list(set(cars_list))


def parse():
    cars_list = all_cars_links()
    car = []
    for url in cars_list:
        html = get_html(url)
        if html.status_code == 200:
            pages_counter = pages_count(html.text)
            for page in range(1, pages_counter+1):
                print(f'parsing {page} from {pages_counter},url {url}')
                html = get_html(url, params={'page': page})
                car.extend(content(html.text))
            save_file(car, FILE)
    print(len(car))


if __name__ == '__main__':
    parse()

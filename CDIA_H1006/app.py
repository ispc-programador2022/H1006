from flask import Flask
from bs4 import BeautifulSoup
from consultas import create_tables, insert_marca, consulta_marca, insert_auto
from lista_modelos import get_urls
import requests
import sqlite3

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/createdatabase', methods=['POST'])
def create_db():  # put application's code here
    con = sqlite3.connect("./info/autocosmos.db")
    cursor = con.cursor()
    return create_tables(cursor)


@app.route('/populatedatabase', methods=['POST'])
def populate_db():  # put application's code here
    con = sqlite3.connect("./info/autocosmos.db")
    cur = con.cursor()
    for url_catalogo in get_urls():
        website = 'https://www.autocosmos.com.ar' + url_catalogo
        # print('URL: ', website)
        result = requests.get(website)
        content = result.text
        soup = BeautifulSoup(content, 'lxml')
        marca = soup.find('h1', class_='teaser__title')
        # CONTROLAMOS WEB VÁLIDA
        if marca is None:
            continue
        else:
            marca = marca.get_text()
        # INSERT MARCA
        insert_marca(cur, marca)
        # print('insert marca', marca)
        # CONSULTA ID_MARCA
        marca_id = consulta_marca(cur, marca)

        lista = datos = []
        for box in soup.find_all('section', class_='section m-brand'):
            card = box.find_all('div', class_='card model-card')
            for modelo in card:
                nombre = modelo.find('span', class_='model-card__brand').text
                moneda = modelo.find('span', class_='model-card__price-value')
                if moneda is None:
                    moneda = '--'
                    precio = '0'
                else:
                    if 'u$s' in moneda.text[0:3]:
                        moneda = moneda.text[0:3]
                        precio = modelo.find('span', class_='model-card__price-value').text.replace('.', '')[3:]
                    else:
                        moneda = moneda.text[0:1]
                        precio = modelo.find('span', class_='model-card__price-value').text.replace('.', '')[1:]
                tipo = modelo.find('span', class_='model-card__ribbon').text
                origen = modelo.find('span', class_='model-card__origin').find('span').text
                imagen = modelo.find('img')['src']
                lista = [marca_id, nombre, moneda, precio, tipo[0:tipo.find('(') - 1],
                         tipo[tipo.find('(') + 1:tipo.find(')')], origen, imagen]
                datos.append(lista)
        # INSERT DATOS AUTOS
        insert_auto(cur, datos)
    con.close()

    return 'Tablas cargadas'


if __name__ == '__main__':
    app.run(debug=True)

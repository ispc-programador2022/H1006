from flask import Flask, render_template
from bs4 import BeautifulSoup
from consultas import *
from lista_modelos import get_urls
import requests
import sqlite3
import matplotlib.pyplot as plt
import base64
import io

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('home.html')


@app.route('/createdatabase', methods=['GET'])
def create_db():  # put application's code here
    con = sqlite3.connect("./info/autocosmos.db")
    cursor = con.cursor()
    return create_tables(cursor)


@app.route('/populatedatabase', methods=['GET'])
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
                    moneda = 'S/D'
                    precio = '0'
                else:
                    if 'u$s' in moneda.text[0:3]:
                        moneda = moneda.text[0:3]
                        precio = modelo.find('span', class_='model-card__price-value').text.replace('.', '')[3:]
                    else:
                        moneda = 'u$s'  # moneda.text[0:1]
                        precio = str(round(int(modelo.find('span', class_='model-card__price-value').text.replace('.', '')[1:])/300, 2))  # conversion a dolar con una cotizacion blue de $300
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

# img = io.BytesIO()

@app.route('/marcas')
def read_marcas():
    con = sqlite3.connect("./info/autocosmos.db")
    cursor = con.cursor()
    df = total_por_marca(con)
    con.close()

    img = io.BytesIO()
    # grafico de barras
    plt.clf()
    plt.title("Total de vehiculos catalogados por fabricante", fontsize=25, fontweight='bold', color='blue', loc='center', style='italic')
    lista = df.values.tolist()
    for i in range(len(lista)):
        plt.barh(lista[i][0], lista[i][1])
    plt.gcf().set_size_inches(12, 10)
    plt.savefig(img, format='png', dpi=90)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return render_template('grafica.html', imagen={'imagen': plot_url})

@app.route('/categorias')
def read_categorias():
    con = sqlite3.connect("./info/autocosmos.db")
    cursor = con.cursor()
    df = total_por_categoria(con)
    con.close()

    img = io.BytesIO()
    # grafico de torta
    plt.clf()
    plt.title("Distribución de vehiculos por segmentos", fontsize=25, fontweight='bold', color='blue', loc='center', style='italic')
    plt.pie(df['cantidad'].tolist(), labels=df['tipo'].tolist(), autopct='%1.1f%%')
    plt.gcf().set_size_inches(12, 10)
    plt.savefig(img, format='png', dpi=80)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return render_template('grafica.html', imagen={'imagen': plot_url})


@app.route('/categorias/<modelo>')
def read_categorias_modelo(modelo):
    con = sqlite3.connect("./info/autocosmos.db")
    cursor = con.cursor()
    df = precio_por_categoria(con, str(modelo))
    con.close()

    img = io.BytesIO()
    # grafico de puntos
    plt.clf()
    plt.title("Precios de modelos para el segmento " + str(modelo) +" (U$s)", fontsize=25, fontweight='bold', color='blue', loc='center', style='italic')
    plt.scatter(df['precio'], df['marca'], color='brown')
    plt.tick_params(axis='x', rotation=45)
    plt.gcf().set_size_inches(20, 10)
    plt.savefig(img, format='png', dpi=80)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return render_template('grafica.html', imagen={'imagen': plot_url})


@app.route('/marcas/<marca>')
def read_precio_marca(marca):
    con = sqlite3.connect("./info/autocosmos.db")
    cursor = con.cursor()
    df = precio_por_marca(con, str(marca))
    con.close()

    img = io.BytesIO()
    # grafico de puntos
    plt.clf()
    plt.title("Precios de modelos para el fabricante " + str(marca) +" (U$s)", fontsize=25, fontweight='bold', color='blue', loc='center', style='italic')
    plt.plot(df['precio'], df['modelo'], color='r')
    plt.tick_params(axis='x', rotation=45)
    plt.gcf().set_size_inches(20, 10)
    plt.savefig(img, format='png', dpi=80)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return render_template('grafica.html', imagen={'imagen': plot_url})



if __name__ == '__main__':
    app.run(debug = True)

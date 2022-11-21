import pandas as pd

def create_tables(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS marcas (
    	id	INTEGER,
    	nombre	TEXT,
    	PRIMARY KEY(id AUTOINCREMENT)
    );""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS autos (
    	id	INTEGER ,
    	marca_id	INTEGER,
    	modelo	TEXT,
    	moneda	TEXT,
    	precio	TEXT,
    	tipo	TEXT,
    	sub_tipo	TEXT,
    	origen	TEXT,
    	url_img	TEXT,
    	PRIMARY KEY(id AUTOINCREMENT),
    	FOREIGN KEY(marca_id) REFERENCES marcas(id)
    );""")

    return 'Bases creadas exitosamente!'


def insert_marca(cursor, marca):
    cursor.execute('insert into marcas (nombre) values (?)', [marca])
    cursor.connection.commit()


def consulta_marca(cursor, marca):
    cursor.execute('SELECT id FROM marcas where nombre = ?', [marca])
    return cursor.fetchone()[0]


def insert_auto(cursor, datos):
    cursor.executemany('insert into autos (marca_id, modelo, moneda, precio, tipo, sub_tipo, origen, url_img) values (?, ?, ?, ?, ?, ?, ?, ?)', [info for info in datos])
    cursor.connection.commit()


def total_por_marca(con):
    df = pd.read_sql_query('''select m.nombre as marca, count(*) as cantidad
                                from autos a 
                                join marcas m 
                                on a.marca_id =m.id 
                                group by m.nombre 
                                ORDER by 1;''', con)
    return df


def total_por_categoria(con):
    df = pd.read_sql_query('''select a.tipo, count(*) as cantidad
                                from autos a 
                                where a.precio > 0
                                group by  a.tipo
                                ORDER by 1;''', con)
    return df


def precio_por_categoria(con, modelo):
    df = pd.read_sql_query('''select m.nombre || ": " || a.modelo as marca, a.precio as precio, a.tipo
                                from autos a join marcas m on a.marca_id =m.id 
                                and a.precio > 0 and a.tipo = "''' + modelo + '''"
                                group by a.tipo,a.moneda ,m.nombre order by 2;''', con)
    return df


def precio_por_marca(con, marca):
    df = pd.read_sql_query('''select a.modelo, a.precio as precio
                                from autos a join marcas m on a.marca_id =m.id 
                                and a.precio > 0 and m.nombre = "''' + marca + '''"
                                ORDER by 2;''', con)
    return df


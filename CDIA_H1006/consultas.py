

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


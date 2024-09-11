from api_client import fetch_data_from_api, initialize_session
from database import Database
from config import COOPERATIVA_BASE_URI, COOPERATIVA_LOGIN_URI


def getArticlesFromDb():
    db = Database()
    db.connect_to_db()

    articlesFromDbQuery = '''
        SELECT *
        FROM articles
        Where categoria is not null
    '''
    
    articlesFromDb = db.execute_query(articlesFromDbQuery)

    # Cerrar la conexión a la base de datos
    db.close_connection()
    return articlesFromDb

def getCategoriesFromDb():
    db = Database()
    db.connect_to_db()

    articlesFromDbQuery = '''
        SELECT id, descripcion
        FROM categorias
    '''
    
    articlesFromDb = db.execute_query(articlesFromDbQuery)

    # Cerrar la conexión a la base de datos
    db.close_connection()
    return articlesFromDb
def createCategoriesDictionaryFromList(categories):
    categories_dictionary = {}

    for category in categories:
        categories_dictionary[category['descripcion']] = category['id']
    
    return categories_dictionary


def getPricesFromBusiness(articles):

    session = initialize_session(COOPERATIVA_LOGIN_URI)
    if articles:
            db = Database()
            db.connect_to_db()
            for article in articles:
                articleFromApi = fetch_data_from_api(session, f"{COOPERATIVA_BASE_URI}articulo/articuloController/articulo_detalle?cod_interno={article['externalreference']}&simple=false")
                if articleFromApi['mensaje'] == 'Articulo solicitado correctamente':

                    # Insertar un registro
                    db.insert_record('precios_historicos', {'precio': articleFromApi['datos']['precio'], 'precio_promo': articleFromApi['datos']['precio_promo'], 'precio_anterior': articleFromApi['datos']['precio_anterior'], 'precio_unitario': articleFromApi['datos']['precio_unitario'], 'article_id': article['articleid'], 'business_id': article['businessid']})
                else:
                     print(f"Error buscando {article['nombre']}-{article['externalreference']}, {articleFromApi['mensaje']}")
            db.close_connection()
    print(f"Insertados {len(articles)}")

def main():
    # Inicializar la sesión para manejar las cookies
    # conn = connect_to_db()
    articles = getArticlesFromDb()
    categories = getCategoriesFromDb()
    categories_dict = createCategoriesDictionaryFromList(categories)

    db = Database()
    db.connect_to_db()
    for article in articles:
        if article['categoria'] in categories_dict:
            db.insert_record('articulos_categorias', {'articulo_id': article['id'],'categoria_id': categories_dict[ article['categoria']]})
        
        if article['categoria_secundaria'] in categories_dict:
            db.insert_record('articulos_categorias', {'articulo_id': article['id'],'categoria_id': categories_dict[article['categoria_secundaria']]})
        
        if article['categoria_terciaria'] in categories_dict:
            db.insert_record('articulos_categorias', {'articulo_id': article['id'],'categoria_id': categories_dict[article['categoria_terciaria']]})
    db.close_connection()
    # getPricesFromBusiness(articles)
    # session = initialize_session()
    
    # # Llamadas a la API reutilizando la misma sesión
    # data1 = fetch_data_from_api(session, "https://www.lacoopeencasa.coop/ws/index.php/articulo/articuloController/articulo_detalle?cod_interno=298783&simple=false")
    # data2 = fetch_data_from_api(session, "https://www.lacoopeencasa.coop/ws/index.php/articulo/articuloController/articulo_detalle?cod_interno=298783&simple=true")

    # Conexión a la base de datos y ejecución de consultas
    
    # if conn is not None:
    #     execute_query(conn, "INSERT INTO tu_tabla (columna1, columna2) VALUES (%s, %s)", data1)
    #     execute_query(conn, "INSERT INTO tu_tabla (columna1, columna2) VALUES (%s, %s)", data2)
    #     conn.close()

if __name__ == "__main__":
    main()


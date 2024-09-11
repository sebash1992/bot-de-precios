from api_client import fetch_data_from_api, initialize_session
from database import Database
from config import COOPERATIVA_BASE_URI, COOPERATIVA_LOGIN_URI


def getArticlesFromDb():
    db = Database()
    db.connect_to_db()

    articlesFromDbQuery = '''
        SELECT nombre, article_business.externalreference, article_business.articleid, article_business.businessid
        FROM articles
        JOIN article_business
            ON articles.id = article_business.articleid
        WHERE externalreference IS NOT NULL
    '''
    
    articlesFromDb = db.execute_query(articlesFromDbQuery)

    # Cerrar la conexión a la base de datos
    db.close_connection()
    return articlesFromDb

def getPricesFromBusiness(articles):

    session = initialize_session(COOPERATIVA_LOGIN_URI)
    if articles:
            db = Database()
            db.connect_to_db()
            for article in articles:
                articleFromApi = fetch_data_from_api(session, f"{COOPERATIVA_BASE_URI}articulo/articuloController/articulo_detalle?cod_interno={article['externalreference']}&simple=false")
                if articleFromApi != None and articleFromApi['mensaje'] == 'Articulo solicitado correctamente':

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
    getPricesFromBusiness(articles)
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


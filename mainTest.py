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
    print(f"Tests")
if __name__ == "__main__":
    main()


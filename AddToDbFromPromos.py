from api_client import fetch_data_from_api, initialize_session
from database import Database
from config import COOPERATIVA_BASE_URI, COOPERATIVA_LOGIN_URI


def getArticlesFromDb():
    db = Database()
    db.connect_to_db()

    articlesFromDbQuery = '''
        SELECT id,nombre, article_business.externalreference, article_business.articleid, article_business.businessid
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
    articlesFromPrincipal = fetch_data_from_api(session, f"{COOPERATIVA_BASE_URI}contenido/ContenidoController/articulos_sector?tag=slider-articulos-secundario")
    articlesFromSecondary = fetch_data_from_api(session, f"{COOPERATIVA_BASE_URI}contenido/ContenidoController/articulos_sector?tag=slider-articulos-principal")
                
    db = Database()
    db.connect_to_db()
    if articlesFromPrincipal:
            for article in articlesFromPrincipal['datos']:
                table_name = 'article_business'
                columns = ['externalreference', 'articleid']
                condition = "externalreference = %s"
                condition_params = (article['cod_interno'],)

                # Obtener los registros que cumplen con la condición
                records = db.select_records(table_name, columns, condition, condition_params)
                if len(records) == 0:
                    articleFromApi = fetch_data_from_api(session, f"{COOPERATIVA_BASE_URI}articulo/articuloController/articulo_detalle?cod_interno={article['cod_interno']}&simple=false")
                    db.insert_record('articles', {'nombre': article['descripcion'],'categoria': articleFromApi['datos']['categoria_inicial_desc'],'categoria_secundaria': articleFromApi['datos']['categoria_secundaria_desc'],'categoria_terciaria': articleFromApi['datos']['categoria_terciaria_desc']})
                

                    table_name = 'articles'
                    columns = ['id']
                    condition = "nombre = %s"
                    condition_params = (article['descripcion'],)
                    records = db.select_records(table_name, columns, condition, condition_params)
                    if len(records) != 0:
                        db.insert_record('article_business', {'articleid': records[0],'externalreference': article['cod_interno'],'businessid': 1})
    if articlesFromSecondary:
            for article in articlesFromSecondary['datos']:
                table_name = 'article_business'
                columns = ['externalreference', 'articleid']
                condition = "externalreference = %s"
                condition_params = (article['cod_interno'],)

                # Obtener los registros que cumplen con la condición
                records = db.select_records(table_name, columns, condition, condition_params)
                if len(records) == 0:
                    articleFromApi = fetch_data_from_api(session, f"{COOPERATIVA_BASE_URI}articulo/articuloController/articulo_detalle?cod_interno={article['cod_interno']}&simple=false")
                    db.insert_record('articles', {'nombre': article['descripcion'],'categoria': articleFromApi['datos']['categoria_inicial_desc'],'categoria_secundaria': articleFromApi['datos']['categoria_secundaria_desc'],'categoria_terciaria': articleFromApi['datos']['categoria_terciaria_desc']})
                

                    table_name = 'articles'
                    columns = ['id']
                    condition = "nombre = %s"
                    condition_params = (article['descripcion'],)
                    records = db.select_records(table_name, columns, condition, condition_params)
                    if len(records) != 0:
                        db.insert_record('article_business', {'articleid': records[0],'externalreference': article['cod_interno'],'businessid': 1})

    db.close_connection()


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


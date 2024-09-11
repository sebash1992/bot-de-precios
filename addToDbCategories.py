from api_client import fetch_data_from_api, initialize_session
from database import Database
from config import COOPERATIVA_BASE_URI, COOPERATIVA_LOGIN_URI


# def getArticlesFromDb():
#     db = Database()
#     db.connect_to_db()

#     articlesFromDbQuery = '''
#         SELECT id,nombre, article_business.externalreference, article_business.articleid, article_business.businessid
#         FROM articles
#         JOIN article_business
#             ON articles.id = article_business.articleid
#         WHERE externalreference IS NOT NULL
#     '''
    
#     articlesFromDb = db.execute_query(articlesFromDbQuery)

#     # Cerrar la conexión a la base de datos
#     db.close_connection()
#     return articlesFromDb

def fillArticles():

    session = initialize_session(COOPERATIVA_LOGIN_URI)
    categoriesFromApi = fetch_data_from_api(session, f"{COOPERATIVA_BASE_URI}/categoria/categoriaController/categorias_plano")
                
    if categoriesFromApi:
            db = Database()
            db.connect_to_db()
            for category in categoriesFromApi['datos']:
                #articleFromApi = fetch_data_from_api(session, f"{COOPERATIVA_BASE_URI}articulo/articuloController/articulo_detalle?cod_interno={article['externalreference']}&simple=false")
                update_query = f"INSERT INTO categorias VALUES ({category['id_categoria']}, {category['id_categoria_padre']}, '{category['descripcion']}')"
               
                db.execute_query(update_query)
            db.close_connection()

def main():
    # Inicializar la sesión para manejar las cookies
    # conn = connect_to_db()
    fillArticles()
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


from apiCliente import ApiClient
from database import Database
from config import COOPERATIVA_BASE_URI, COOPERATIVA_LOGIN_URI


def getArticlesFromDb():
    db = Database()
    db.connect_to_db()

    articlesFromDbQuery = '''
        SELECT articles.id,nombre, article_business.externalreference, article_business.articleid, article_business.businessid
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
    if articles:
            db = Database()
            db.connect_to_db()
            for article in articles:
                api_client = ApiClient(base_url='https://www.vea.com.ar')

                # Obtener información del producto por SKU
                try:
                    product_info = api_client.get_product_by_sku(article['externalreference'])
                    print("Información del producto:", product_info)
                except Exception as e:
                    print(f"Error en la solicitud: {e}")

                # Cerrar el cliente API
                api_client.close()
                if product_info != None and len(product_info)>0:

                    # Insertar un registro
                    precio = product_info[0]['items'][0]['sellers'][0]['commertialOffer']['Price']
                    db.insert_record('precios_historicos', {'precio': precio, 'article_id': article['articleid'], 'business_id': article['businessid']})
                
                    # categories = product_info[0]['categories'][0].split("/")
                    # categoriesId = product_info[0]['categoriesIds'][0].split("/")
                    # for indice, category in enumerate(categories):
                    #      if category != '':
                    #             table_name = 'categorias'
                    #             columns = ['id']
                    #             condition = "id = %s"
                    #             condition_params = (categoriesId[indice],)
                    #             records = db.select_records(table_name, columns, condition, condition_params)
                    #             if len(records) == 0:
                    #                  update_query = f"INSERT INTO categorias VALUES ({categoriesId[indice]}, 0, '{category}')"
                    #                  db.execute_query(update_query)
                    #             articleId = article['id']     
                    #             catId = int(categoriesId[indice])
                    #             db.insert_record('articulos_categorias', {'articulo_id': articleId, 'categoria_id': catId}) 
                
                else:
                     print(f"Error buscando {article['nombre']}-{article['externalreference']}, {article['nombre']}")
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


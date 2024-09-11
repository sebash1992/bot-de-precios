from api_client import fetch_data_from_api, initialize_session, post_from_api
from database import Database
from config import COOPERATIVA_BASE_URI, COOPERATIVA_LOGIN_URI



def getPricesFromBusiness():

    session = initialize_session(COOPERATIVA_LOGIN_URI)
    page = 0
    category = 905
    json_body = {
        "id_busqueda": category,
        "pagina": page,
        "filtros": {
        "preciomenor": -1,
        "preciomayor": -1,
        "marca": [],
        "categoria": [],
        "tipo_seleccion": "categoria",
        "filtros_gramaje": [],
        "cant_articulos": 0,
        "ofertas": False,
        "modificado": False,
        "primer_filtro": ""
        }
    }
    articleList = []
    articlesFromCategory = post_from_api(session, f"{COOPERATIVA_BASE_URI}categoria/categoriaController/categorias_filtrado",None,json_body)
    articleList = articleList + articlesFromCategory['datos']['articulos']
    while(len(articleList) < articlesFromCategory['datos']['cantidad_articulos']):
        page+=1
        json_body = {
            "id_busqueda": category,
            "pagina": page,
            "filtros": {
            "preciomenor": -1,
            "preciomayor": -1,
            "marca": [],
            "categoria": [],
            "tipo_seleccion": "categoria",
            "filtros_gramaje": [],
            "cant_articulos": 0,
            "ofertas": False,
            "modificado": False,
            "primer_filtro": ""
            }
        }
        articlesFromCategory = post_from_api(session, f"{COOPERATIVA_BASE_URI}categoria/categoriaController/categorias_filtrado",None,json_body)
        articleList = articleList + articlesFromCategory['datos']['articulos']
    db = Database()
    db.connect_to_db()
    if articleList:
            for article in articleList:
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
    getPricesFromBusiness()
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


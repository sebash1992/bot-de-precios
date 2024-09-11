import argparse
import requests
import base64
import json
from database import Database
import time


def make_request(variables):
    # Codificar las variables a Base64
    variables_json = json.dumps(variables)
    encoded_variables = base64.b64encode(variables_json.encode('utf-8')).decode('utf-8')
    
    # Construir la URL del endpoint
    base_url = "https://www.carrefour.com.ar/_v/segment/graphql/v1"
    params = {
        "workspace": "master",
        "maxAge": "short",
        "appsEtag": "remove",
        "domain": "store",
        "locale": "es-AR",
        "__bindingId": "ecd0c46c-3b2a-4fe1-aae0-6080b7240f9b",
        "operationName": "productSearchV3",
        "variables": json.dumps({}),
        "extensions": json.dumps({
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "8e3fd5f65d7d83516bfea23051b11e7aa469d85f26906f27e18afbee52c56ce4",
                "sender": "vtex.store-resources@0.x",
                "provider": "vtex.search-graphql@0.x"
            },
            "variables": encoded_variables
        })
    }
    
    # Hacer el request
    response = requests.get(base_url, params=params)
    
    # Verificar si el request fue exitoso
    if response.status_code == 200:
        print("Datos de la respuesta:")
        return response.json()
    else:
        print(f"Error en la solicitud: {response.status_code} - {response.text}")
        return None
    
def generate_graphql_query(query, from_index, to_index):

    variables = {
        "hideUnavailableItems": True,
        "skusFilter": "ALL_AVAILABLE",
        "simulationBehaviour": "default",
        "installmentCriteria": "MAX_WITHOUT_INTEREST",
        "productOriginVtex": False,
        "map": "c,c",
        "query": query,
        "orderBy": "OrderByScoreDESC",
        "from": from_index,
        "to": to_index,
        "selectedFacets": [
            {"key": "c", "value": query},
            # {"key": "c", "value": "espumantes-y-sidras"}
        ],
        "facetsBehaviour": "Static",
        "categoryTreeBehavior": "default",
        "withFacets": False,
        "variant": "null-null",
        "advertisementOptions": {
            "showSponsored": False,
            "sponsoredCount": 0,
            "advertisementPlacement": "top_search",
            "repeatSponsoredProducts": False
        }
    }
    return make_request(variables)

def main(parametro):
    print(f"El parámetro recibido es: {parametro}")
    # Aquí va la lógica principal de tu script
    # Aquí puedes modificar las variables para hacer diferentes consultas
    allProductList = []
    from_index = 0
    to_index = 49
    # categorias = ["Bebidas","Almacen","Lacteos-y-productos-frescos","Carnes-y-Pescados","Frutas-y-Verduras","Panaderia","Congelados","Limpieza","Perfumeria","Mascotas"] #"Desayuno-y-merienda"
    categorias = [parametro]
    for categoria in categorias:
        productList = []
        while True:
            # Código que quieres ejecutar
            products = generate_graphql_query(query=categoria, from_index=from_index, to_index=to_index)
            if products != None and products['data']['productSearch'] != None:
                recordsFiltered = products['data']['productSearch']['recordsFiltered']
                # recordsFiltered = 10
                print(recordsFiltered)
                productList = productList + products['data']['productSearch']['products']
                if len(products['data']['productSearch']['products']) > 0: 
                    from_index = to_index + 1
                    to_index = to_index + 50
            # Condición de salida (simulando 'until')
            if recordsFiltered <= len(productList) or  2500 <= len(productList):
                allProductList = allProductList + productList
                break
    
    db = Database()
    db.connect_to_db()              
    for product in productList:

        table_name = 'article_business'
        columns = ['articleid',"externalreference"]
        condition = "externalreference = %s"
        condition_params = (product['items'][0]['itemId'],)
        articlesInDb = db.select_records(table_name, columns, condition, condition_params)

        if len(articlesInDb) != 0:

            articleId = articlesInDb[0][0]
            
            
            precio = product['items'][0]['sellers'][0]['commertialOffer']['Price']
            db.insert_record('precios_historicos', {'precio': precio, 'article_id': articleId, 'business_id': 1})
      

    db.close_connection()    









if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Este es un script de ejemplo que recibe un parámetro.")
    parser.add_argument("parametro", help="El parámetro que se pasará al script.")
    
    args = parser.parse_args()
    main(args.parametro)
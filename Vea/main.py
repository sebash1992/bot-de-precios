import requests
import json
import base64
from database import Database

# Función para codificar variables a Base64
def encode_to_base64(data):
    json_string = json.dumps(data)
    return base64.b64encode(json_string.encode('utf-8')).decode('utf-8')

# Función para construir la consulta GraphQL
def generate_graphql_query(query, from_index, to_index):
    variables = {
        "hideUnavailableItems": True,
        "skusFilter": "ALL",
        "simulationBehavior": "default",
        "installmentCriteria": "MAX_WITHOUT_INTEREST",
        "productOriginVtex": False,
        "map": "c",
        "query": query,
        "orderBy": "OrderByScoreDESC",
        "from": from_index,
        "to": to_index,
        "selectedFacets": [{"key": "c", "value": query}],
        "facetsBehavior": "Static",
        "categoryTreeBehavior": "default",
        "withFacets": False,
        "advertisementOptions": {
            "showSponsored": True,
            "sponsoredCount": 0,
            "advertisementPlacement": "top_search",
            "repeatSponsoredProducts": True
        }
    }

    extensions = {
        "persistedQuery": {
            "version": 1,
            "sha256Hash": "8e3fd5f65d7d83516bfea23051b11e7aa469d85f26906f27e18afbee52c56ce4",
            "sender": "vtex.store-resources@0.x",
            "provider": "vtex.search-graphql@0.x"
        },
        "variables": encode_to_base64(variables)
    }

    return extensions

def fetch_products(query, from_index, to_index):
    graphql_endpoint = "https://www.vea.com.ar/_v/segment/graphql/v1"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    extensions = generate_graphql_query(query, from_index, to_index)
    
    # Armando la solicitud completa con todas las partes requeridas
    params = {
        "workspace": "master",
        "maxAge": "short",
        "appsEtag": "remove",
        "domain": "store",
        "locale": "es-AR",
        "__bindingId": "6890cd39-87c6-4689-ad4f-3b913f3c0b19",
        "operationName": "productSearchV3",
        "variables": json.dumps({}),  # Este campo se mantiene como un objeto JSON vacío
        "extensions": json.dumps(extensions)
    }

    response = requests.get(graphql_endpoint, headers=headers, params=params)

    # Revisar la respuesta de la API
    if response.status_code == 200:
        print("Solicitud exitosa. Respuesta de la API:")
       # print(response['data']['productSearch']['products'])
    else:
        print(f"Error en la solicitud: {response.status_code}")
        #print(response.text)

    return response.json()

# Ejemplo de uso
productList = []
from_index = 0
to_index = 49
categoria = "mascotas"
while True:
    # Código que quieres ejecutar
    products = fetch_products(query=categoria, from_index=from_index, to_index=to_index)
    recordsFiltered = products['data']['productSearch']['recordsFiltered']
    # recordsFiltered = 10
    productList = productList + products['data']['productSearch']['products']
    from_index = to_index + 1
    to_index = to_index + 50
    # Condición de salida (simulando 'until')
    if recordsFiltered <= len(productList):
        break
# db.insert_record('articles', {'nombre': article['descripcion'],'categoria': articleFromApi['datos']['categoria_inicial_desc'],'categoria_secundaria': articleFromApi['datos']['categoria_secundaria_desc'],'categoria_terciaria': articleFromApi['datos']['categoria_terciaria_desc']})
db = Database()
db.connect_to_db()
categoryId =productList[0]['categoryId']
                  
for product in productList:
    db.insert_record('articles', {'nombre': product['productName'],'categoria': categoria})

    table_name = 'articles'
    columns = ['id']
    condition = "nombre = %s"
    condition_params = (product['productName'],)
    records = db.select_records(table_name, columns, condition, condition_params)

    db.insert_record('article_business', {'articleid': records[0],'externalreference': product['items'][0]['itemId'],'businessid': 1})    

           

db.close_connection()         


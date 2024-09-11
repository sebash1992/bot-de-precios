import requests

class ApiClient:
    def __init__(self, base_url, headers=None, cookies=None):
        """
        Inicializa el cliente API.
        :param base_url: La URL base de la API.
        :param headers: Cabeceras por defecto para las solicitudes.
        :param cookies: Cookies por defecto para las solicitudes.
        """
        self.base_url = base_url
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)
        if cookies:
            self.session.cookies.update(cookies)

    def get(self, endpoint, params=None):
        """
        Realiza una solicitud GET a un endpoint especificado.
        :param endpoint: El endpoint de la API.
        :param params: Parámetros de consulta opcionales.
        :return: Respuesta de la solicitud.
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()  # Lanza un error para códigos de estado HTTP no exitosos
        return response

    def post(self, endpoint, data=None, json=None):
        """
        Realiza una solicitud POST a un endpoint especificado.
        :param endpoint: El endpoint de la API.
        :param data: Datos para enviar en el cuerpo de la solicitud (usualmente para formularios).
        :param json: Datos para enviar en el cuerpo de la solicitud en formato JSON.
        :return: Respuesta de la solicitud.
        """
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, data=data, json=json)
        response.raise_for_status()  # Lanza un error para códigos de estado HTTP no exitosos
        return response

    def get_product_by_sku(self, sku_id):
        """
        Realiza una solicitud GET al endpoint de búsqueda de productos utilizando un SKU específico.
        :param sku_id: El ID del SKU del producto que se desea buscar.
        :return: Respuesta de la solicitud.
        """
        endpoint = f"/api/catalog_system/pub/products/search?fq=skuId:{sku_id}"
        response = self.get(endpoint)
        return response.json()  # Devuelve la respuesta en formato JSON

    def close(self):
        """
        Cierra la sesión del cliente.
        """
        self.session.close()

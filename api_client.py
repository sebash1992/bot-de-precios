import requests
from config import API_ENDPOINT,COOPERATIVA_LOGIN_URI

# Inicializa una sesión de requests
def initialize_session(loginEndpoint):
    session = requests.Session()
    try:
        # Realiza una llamada inicial si necesitas autenticarte o iniciar sesión
        response = session.post(loginEndpoint)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al inicializar la sesión: {e}")
        session = None
    return session

# Función para hacer solicitudes usando la sesión persistente
def fetch_data_from_api(session, endpoint):
    if session is None:
        print("La sesión no está inicializada.")
        return None
    try:
        response = session.get(endpoint)
        response.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa
        return response.json()  # Devuelve la respuesta en formato JSON
    except requests.exceptions.RequestException as e:
        print(f"Error al llamar a la API: {e}")
        return None
    
def post_from_api(session, endpoint,data=None, json=None):
    if session is None:
        print("La sesión no está inicializada.")
        return None
    try:
        response = session.get(endpoint)

        response = session.post(endpoint, data=data, json=json)
        response.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa
        return response.json()  # Devuelve la respuesta en formato JSON
    except requests.exceptions.RequestException as e:
        print(f"Error al llamar a la API: {e}")
        return None

import tweepy
from database import Database
from config import TWITTER_API_KEY, TWITTER_API_SECRET_KEY, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET

def fetch_data_from_db():
    """
    Conecta a la base de datos y recupera los datos.
    """
    db = Database()
    db.connect_to_db()

    # Ejemplo de consulta para recuperar datos
    query = '''
        select articles.nombre,precio,precio_anterior
        from precios_historicos join articles
            on article_id = articles.id
    '''
    articles_from_db = db.execute_query(query)
    db.close_connection()

    return articles_from_db

def tweet_results(results):
    """
    Twittea los resultados en tu cuenta de Twitter.
    """
    # Autenticar con la API de Twitter
    client = tweepy.Client(
        consumer_key=TWITTER_API_KEY, consumer_secret=TWITTER_API_SECRET_KEY,
        access_token=TWITTER_ACCESS_TOKEN, access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
    )

    try:
        # Construir el mensaje del tweet
        for article in results:
            tweet_text = f"Artículo: {article['nombre']}, Precio: {article['precio']}"
            response = client.create_tweet(
            text="This Tweet was Tweeted using Tweepy and Twitter API v2!")
            print(f"Twitteado: {tweet_text}")
    except tweepy.errors.TweepyException as e:
        print(f"Error al twittear: {e}")

def main():
    # Obtener datos de la base de datos
    results = fetch_data_from_db()

    # Twittear los resultados
    if results:
        tweet_results(results)
    else:
        print("No hay resultados para twittear.")

if __name__ == "__main__":
    main()

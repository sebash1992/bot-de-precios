import argparse
import tweepy
from Utils.database import Database
from Utils.tweet import Tweet
from Utils.config import DB_HOST, CO_DB_NAME,VEA_DB_NAME,CARREFOUR_DB_NAME, DB_USER, DB_PASS,TWITTER_API_KEY, TWITTER_API_SECRET_KEY, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
from datetime import datetime, timedelta
import locale

def ejecutar_query_diferencia_categorias_entre_fechas(categoria_ids, day_from, day_to, connection):
        query = f"""
        WITH precios_dia_uno AS (
            SELECT
                c.descripcion AS categoria_nombre,
                ac.categoria_id,
                SUM(ph.precio) AS precio_total_dia_uno
            FROM
                public.precios_historicos ph
            JOIN
                public.articles a ON ph.article_id = a.id
            JOIN
                public.articulos_categorias ac ON a.id = ac.articulo_id
            JOIN
                public.categorias c ON ac.categoria_id = c.id
            WHERE
                ph.lastupdate::date = '{day_from}'  -- Fecha del día 1
                AND ac.categoria_id IN ({', '.join(map(str, categoria_ids))})  -- Filtrar por IDs de categorías
            GROUP BY
                ac.categoria_id, c.descripcion
        ),
        precios_dia_dos AS (
            SELECT
                c.descripcion AS categoria_nombre,
                ac.categoria_id,
                SUM(ph.precio) AS precio_total_dia_dos
            FROM
                public.precios_historicos ph
            JOIN
                public.articles a ON ph.article_id = a.id
            JOIN
                public.articulos_categorias ac ON a.id = ac.articulo_id
            JOIN
                public.categorias c ON ac.categoria_id = c.id
            WHERE
                ph.lastupdate::date = '{day_to}'  -- Fecha del día 2
                AND ac.categoria_id IN ({', '.join(map(str, categoria_ids))})  -- Filtrar por las mismas categorías
            GROUP BY
                ac.categoria_id, c.descripcion
        )
        SELECT
            COALESCE(pdu.categoria_nombre, pdd.categoria_nombre) AS categoria_nombre,
            COALESCE(SUM(pdd.precio_total_dia_dos) - SUM(pdu.precio_total_dia_uno), 0) AS diferencia_precio,
            COALESCE((SUM(pdd.precio_total_dia_dos) - SUM(pdu.precio_total_dia_uno)) / SUM(pdu.precio_total_dia_uno) * 100, 0) AS diferencia_porcentual
        FROM
            precios_dia_uno pdu
        FULL OUTER JOIN
            precios_dia_dos pdd
        ON
            pdu.categoria_id = pdd.categoria_id
        GROUP BY
            COALESCE(pdu.categoria_nombre, pdd.categoria_nombre);
        """
        return connection.execute_query(query)

def ejecutar_query_diferencia_entre_fechas( day_from, day_to, connection):
        query = f"""
        WITH precios_dia_uno AS (
            SELECT
                SUM(ph.precio) AS precio_total_dia_uno
            FROM
                public.precios_historicos ph
            WHERE
                ph.lastupdate::date = '{day_from}'  -- Fecha del día 1
        ),
        precios_dia_dos AS (
            SELECT
                SUM(ph.precio) AS precio_total_dia_dos
            FROM
                public.precios_historicos ph
            WHERE
                ph.lastupdate::date = '{day_to}'  -- Fecha del día 2
        )
        SELECT
            COALESCE(pdd.precio_total_dia_dos - pdu.precio_total_dia_uno, 0) AS diferencia_precio,
            COALESCE((pdd.precio_total_dia_dos - pdu.precio_total_dia_uno) / pdu.precio_total_dia_uno * 100, 0) AS diferencia_porcentual
        FROM
            precios_dia_uno pdu,
            precios_dia_dos pdd;

        """
        return connection.execute_query(query)

def crearTweet(diferencias, textoInicial):
     tweet=textoInicial+"\n"
     for differencia in diferencias:
        tweet+= f"{differencia['categoria_nombre']}: {round(differencia['diferencia_porcentual'], 2)}%\n"
     return tweet;   
def postTweet(tweet):
    client = tweepy.Client(
        consumer_key=TWITTER_API_KEY, consumer_secret=TWITTER_API_SECRET_KEY,
        access_token=TWITTER_ACCESS_TOKEN, access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
    )
    try:
        return client.create_tweet(text=tweet)
    except tweepy.errors.TweepyException as e:
        print(f"Error al twittear: {e}")

def GetPriceDifferenceLastWeekByCategory():
    db_cooperativa = Database()
    db_cooperativa.connect_to_db(DB_HOST,CO_DB_NAME,DB_USER,DB_PASS)
    categorias_cooperativa = [2,3,4,5,6]
    db_vea = Database()
    db_vea.connect_to_db(DB_HOST,VEA_DB_NAME,DB_USER,DB_PASS)
    categorias_vea = [1,2,4,3,7,11,457,13,6,9] # 8,14
    db_carrefour = Database()
    db_carrefour.connect_to_db(DB_HOST,CARREFOUR_DB_NAME,DB_USER,DB_PASS)
    categorias_carrefour = [38,189,1,86,116,123,128,150,237] #140,226

    hoy = datetime.now()
    hace_7_dias = hoy - timedelta(days=7)

    tweet_client = Tweet()
    tweet_client.connect_client(TWITTER_API_KEY,TWITTER_API_SECRET_KEY,TWITTER_ACCESS_TOKEN,TWITTER_ACCESS_TOKEN_SECRET)
    diferenciasCooperativa = ejecutar_query_diferencia_categorias_entre_fechas(categorias_cooperativa,hoy.strftime('%Y-%m-%d'),hace_7_dias.strftime('%Y-%m-%d'),db_cooperativa)
    tweet =  crearTweet(diferenciasCooperativa,f"Variacion de precios la Cooperativa Obrera durante la ultima semana")
    result = tweet_client.post(tweet)
    
    
    diferenciasVea = ejecutar_query_diferencia_categorias_entre_fechas(categorias_vea,hoy.strftime('%Y-%m-%d'),hace_7_dias.strftime('%Y-%m-%d'),db_vea)
    tweet = crearTweet(diferenciasVea,f"Variacion de precios en Vea durante la ultima semana")
    longitud = len(tweet)
    result = tweet_client.post(tweet)

    diferenciasCarrefour = ejecutar_query_diferencia_categorias_entre_fechas(categorias_carrefour,hoy.strftime('%Y-%m-%d'),hace_7_dias.strftime('%Y-%m-%d'),db_carrefour)
    tweet = crearTweet(diferenciasCarrefour,f"Variacion de precios en Carrefour durante la ultima semana")
    longitud = len(tweet)
    result = tweet_client.post(tweet)

    return 1

def GetPriceDifferenceDuringMonth():
    db_cooperativa = Database()
    db_cooperativa.connect_to_db(DB_HOST,CO_DB_NAME,DB_USER,DB_PASS)
    categorias_cooperativa = [2,3,4,5,6]
    db_vea = Database()
    db_vea.connect_to_db(DB_HOST,VEA_DB_NAME,DB_USER,DB_PASS)
    categorias_vea = [1,2,4,3,7,11,457,13,6,9] # 8,14
    db_carrefour = Database()
    db_carrefour.connect_to_db(DB_HOST,CARREFOUR_DB_NAME,DB_USER,DB_PASS)
    categorias_carrefour = [38,189,1,86,116,123,128,150,237] #140,226

    hoy = datetime.now()
    principio_de_mes=hoy.replace(day=2)
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8') 
    tweet_client = Tweet()
    tweet_client.connect_client(TWITTER_API_KEY,TWITTER_API_SECRET_KEY,TWITTER_ACCESS_TOKEN,TWITTER_ACCESS_TOKEN_SECRET)
    diferenciasCooperativa = ejecutar_query_diferencia_categorias_entre_fechas(categorias_cooperativa,principio_de_mes.strftime('%Y-%m-%d'),hoy.strftime('%Y-%m-%d'),db_cooperativa)
    tweet =  crearTweet(diferenciasCooperativa,f"Variacion de precios al {principio_de_mes.strftime('%d %B')} en Cooperativa Obrera 🛒:")
    result = tweet_client.post(tweet)
    
    
    diferenciasVea = ejecutar_query_diferencia_categorias_entre_fechas(categorias_vea,principio_de_mes.strftime('%Y-%m-%d'),hoy.strftime('%Y-%m-%d'),db_vea)
    tweet = crearTweet(diferenciasVea,f"Variacion de precios al {principio_de_mes.strftime('%d %B')} en Vea 🛒:")
    longitud = len(tweet)
    result = tweet_client.post(tweet)

    diferenciasCarrefour = ejecutar_query_diferencia_categorias_entre_fechas(categorias_carrefour,principio_de_mes.strftime('%Y-%m-%d'),hoy.strftime('%Y-%m-%d'),db_carrefour)
    tweet = crearTweet(diferenciasCarrefour,f"Variacion de precios al {principio_de_mes.strftime('%d %B')} en Carrefour 🛒:")
    longitud = len(tweet)
    result = tweet_client.post(tweet)

    return 1

def GetPriceDifferenceBetweenDates(desde ,hasta):
    db_cooperativa = Database()
    db_cooperativa.connect_to_db(DB_HOST,CO_DB_NAME,DB_USER,DB_PASS)
    db_vea = Database()
    db_vea.connect_to_db(DB_HOST,VEA_DB_NAME,DB_USER,DB_PASS)
    db_carrefour = Database()
    db_carrefour.connect_to_db(DB_HOST,CARREFOUR_DB_NAME,DB_USER,DB_PASS)


    tweet_client = Tweet()
    tweet_client.connect_client(TWITTER_API_KEY,TWITTER_API_SECRET_KEY,TWITTER_ACCESS_TOKEN,TWITTER_ACCESS_TOKEN_SECRET)
    diferenciasCooperativa = ejecutar_query_diferencia_entre_fechas(desde.strftime('%Y-%m-%d'),hasta.strftime('%Y-%m-%d'),db_cooperativa)
    diferenciasVea = ejecutar_query_diferencia_entre_fechas(desde.strftime('%Y-%m-%d'),hasta.strftime('%Y-%m-%d'),db_vea)
    diferenciasCarrefour = ejecutar_query_diferencia_entre_fechas(desde.strftime('%Y-%m-%d'),hasta.strftime('%Y-%m-%d'),db_carrefour)
    tweet = f"Variacion de precios entre el {desde.strftime('%Y-%m-%d')} y el {hasta.strftime('%Y-%m-%d')} 📊:\n"
    tweet+= f"Cooperativa Obrera: {round(diferenciasCooperativa[0]['diferencia_porcentual'],2)}%\n"
    tweet+= f"Vea: {round(diferenciasVea[0]['diferencia_porcentual'],2)}%\n"
    # tweet+= f"Carrefour: {round(diferenciasCarrefour[0]['diferencia_porcentual'],2)}%\n"
    tweet+= f"¿Dónde has notado más cambios en los precios? 🤔\n #Inflación #Precios #EconomíaArgentina #Supermercados #BahiaBlanca"
    tweet_client.post(tweet)

def GetPriceDifferenceInMonth(desde ,hasta):
    db_cooperativa = Database()
    db_cooperativa.connect_to_db(DB_HOST,CO_DB_NAME,DB_USER,DB_PASS)
    db_vea = Database()
    db_vea.connect_to_db(DB_HOST,VEA_DB_NAME,DB_USER,DB_PASS)
    db_carrefour = Database()
    db_carrefour.connect_to_db(DB_HOST,CARREFOUR_DB_NAME,DB_USER,DB_PASS)


    tweet_client = Tweet()
    tweet_client.connect_client(TWITTER_API_KEY,TWITTER_API_SECRET_KEY,TWITTER_ACCESS_TOKEN,TWITTER_ACCESS_TOKEN_SECRET)
    diferenciasCooperativa = ejecutar_query_diferencia_entre_fechas(desde.strftime('%Y-%m-%d'),hasta.strftime('%Y-%m-%d'),db_cooperativa)
    diferenciasVea = ejecutar_query_diferencia_entre_fechas(desde.strftime('%Y-%m-%d'),hasta.strftime('%Y-%m-%d'),db_vea)
    # diferenciasCarrefour = ejecutar_query_diferencia_entre_fechas(desde.strftime('%Y-%m-%d'),hasta.strftime('%Y-%m-%d'),db_carrefour)
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8') 
    tweet = f"Variacion de precios al {hasta.strftime('%d %B')} 🛒 :\n"
    tweet+= f"Cooperativa Obrera: {round(diferenciasCooperativa[0]['diferencia_porcentual'],2)}%\n"
    tweet+= f"Vea: {round(diferenciasVea[0]['diferencia_porcentual'],2)}%\n"
    # tweet+= f"Carrefour: {round(diferenciasCarrefour[0]['diferencia_porcentual'],2)}%\n"
    tweet+= f"¿En qué supermercado sientes que los precios están más estables?.👀\n #Inflación #Precios #EconomíaArgentina #Supermercados #BahiaBlanca"
    tweet_client.post(tweet)


def main(parametro):
    print(f"El parámetro recibido es: {parametro}")
    parametro = 4
    if parametro == 1:
        GetPriceDifferenceLastWeekByCategory()
        return "Opción 1"
    if parametro == 2:
        GetPriceDifferenceDuringMonth()
        return "Opción 1"
    elif parametro == 3:
        hoy = datetime.now()
        hace_7_dias = hoy - timedelta(days=7)
        GetPriceDifferenceBetweenDates(hace_7_dias,hoy)
    elif parametro == 4:
        hoy = datetime.today()
        principio_de_mes = hoy.replace(day=2)
        GetPriceDifferenceInMonth(principio_de_mes,hoy)
        return "Opción 3"
    else:
        return "Opción por defecto" 









if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Este es un script de ejemplo que recibe un parámetro.")
    parser.add_argument("parametro", help="El parámetro que se pasará al script.")
    args = parser.parse_args()
    main(args.parametro)
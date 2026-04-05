import tweepy 

class Tweet:
    def __init__(self):
        self.client = None

    def connect_client(self,api_key,api_secret,access_token,access_token_secret):
        self.client = tweepy.Client(
            consumer_key=api_key, consumer_secret=api_secret,
            access_token=access_token, access_token_secret=access_token_secret
        )
        print("Cliente de TW Creado exitosamente")

    def post(self, text):
        try:
            return self.client.create_tweet(text=text)
        except tweepy.errors.TweepyException as e:
            print(f"Error al twittear: {e}")


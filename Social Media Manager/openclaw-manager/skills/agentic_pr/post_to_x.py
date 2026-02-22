import os
import sys
import tweepy
from dotenv import load_dotenv

def post_to_x(text):
    # Load environment variables from .env file
    load_dotenv()
    
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_secret = os.getenv("ACCESS_SECRET")
    
    if not all([api_key, api_secret, access_token, access_secret]):
        print("Error: Missing X API credentials in .env file.")
        sys.exit(1)
        
    try:
        # Authenticate with V2 API
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )
        
        response = client.create_tweet(text=text)
        print(f"Successfully posted to X! Tweet ID: {response.data['id']}")
        return response.data['id']
    except Exception as e:
        print(f"Error posting to X: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python post_to_x.py \"Your tweet text here\"")
        sys.exit(1)
        
    tweet_text = sys.argv[1]
    post_to_x(tweet_text)

import os
import time
import tweepy
import openai

# ==== AUTH ====
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
API_KEY = os.getenv("TWITTER_API_KEY")
API_KEY_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
openai.api_key = os.getenv("OPENAI_API_KEY")

client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_KEY_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

auth = tweepy.OAuth1UserHandler(API_KEY, API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

BOT_USERNAME = os.getenv("BOT_USERNAME", "your_username")  # without @


# ==== GPT REPLY ====
def generate_reply(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-5-mini",  # or gpt-5
        messages=[{
            "role": "user",
            "content": (
                "use lowercase and act as a witty human. "
                "reply casually without hashtags or links. "
                f"here’s the tweet: {prompt}"
            )
        }],
        max_tokens=100
    )
    return response["choices"][0]["message"]["content"].strip()


# ==== CHECK MENTIONS ====
def check_mentions(since_id):
    mentions = client.get_users_mentions(
        id=client.get_me().data.id,
        since_id=since_id,
        tweet_fields=["author_id", "text"]
    )
    return mentions


# ==== MAIN LOOP ====
def main():
    since_id = None
    print("🤖 bot is running...")
    while True:
        mentions = check_mentions(since_id)
        if mentions and mentions.data:
            for tweet in reversed(mentions.data):
                since_id = tweet.id
                user_text = tweet.text
                user_id = tweet.author_id

                print(f"📨 mention from {user_id}: {user_text}")

                # like the tweet
                client.like(tweet.id)

                # follow if requested
                if "follow me" in user_text.lower():
                    client.follow_user(user_id)
                    print(f"👤 followed {user_id}")

                # generate gpt reply
                reply_text = generate_reply(user_text)

                # reply
                client.create_tweet(
                    text=f"@{BOT_USERNAME} {reply_text}",
                    in_reply_to_tweet_id=tweet.id
                )
                print(f"💬 replied to {tweet.id}")
        time.sleep(30)


if __name__ == "__main__":
    main()

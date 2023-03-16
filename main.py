import tweepy
import openai
import os
import json

# Get API keys and access tokens from environment variables
api_key = os.environ.get("api_key")
api_secret_key = os.environ.get("api_secret_key")
access_token = os.environ.get("access_token")
access_secret_token = os.environ.get("access_secret_token")
chatgpt_key = os.environ.get("chatgpt_key")


class Service:
    """
    A class that handles interactions with Twitter and OpenAI's GPT-3 chatbot API.
    """

    def __init__(self):
        """
        Initializes the Service class by setting up the Twitter API authentication.
        """
        auth = tweepy.OAuth1UserHandler(
            api_key, api_secret_key, access_token, access_secret_token
        )
        self.count = 10
        self.api = tweepy.API(auth)

    def call_gpt(self, post):
        """
        Calls OpenAI's GPT-3 chatbot API to generate a response to a given post.

        Args:
            post (str): The text of the original post to generate a response to.

        Returns:
            str: The generated response text.
        """
        openai.api_key = chatgpt_key
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"roast the post in a funny way in less than 279 characters '{post}'"
                },
            ],
            max_tokens=280,
            n=1,
            stop=None,
            temperature=0.5,
        )
        return res.get("choices")[0].get("message").get("content").strip()

    def handle_mentions(self):
        """
        Handles mentions of the bot account on Twitter by checking for new mentions, generating
        a response using GPT-3, and replying to the original post with the generated response.
        """
        # Load the list of tweet IDs that the bot has already replied to
        with open('replied_tweet_ids.json', 'r') as f:
            try:
                replied_tweet_ids = json.load(f)
            except:
                replied_tweet_ids = []
        mentions = self.api.mentions_timeline(count=self.count)

        for mention in mentions:
            try:
                original_tweet_id = mention.in_reply_to_status_id
                original_tweet = self.api.get_status(original_tweet_id)
                original_tweet_text = original_tweet.text
                mention_text = mention.text
                user_screen_name = mention.user.screen_name
                if '@ElvinJafarov2' in mention_text:
                    if original_tweet_id not in replied_tweet_ids:
                        if original_tweet_text:
                            txt = self.call_gpt(original_tweet_text)

                            if txt:
                                txt = f"@{user_screen_name} " + txt
                                self.api.update_status(
                                    status=txt,
                                    in_reply_to_status_id=mention.id,
                                    auto_populate_reply_metadata=True
                                )
                                replied_tweet_ids.append(original_tweet_id)

            except BaseException as e:
                print(e)

        # Save the updated list of replied tweet IDs
        with open('replied_tweet_ids.json', 'w') as f:
            json.dump(replied_tweet_ids, f)


if __name__ == "__main__":
    serv = Service()
    serv.handle_mentions()

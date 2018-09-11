# -*- coding: utf-8 -*-
"""
Python Slack Bot class modified from the Slack pythOnBoarding app
"""
import os
import time
import message
import cafe.script as cafe
import db.settings_db as db

from slackclient import SlackClient

# To remember which teams have authorized your app and what tokens are
# associated with each team, we can store this information in memory on
# as a global object. When your bot is out of development, it's best to
# save this in a more persistant memory store.

# Only one team (Target Tech Slack) in this case
authed_teams = {}


class Bot(object):
    """ Instantiates a Bot object to handle Slack onboarding interactions."""
    def __init__(self):
        super(Bot, self).__init__()
        self.name = "cafebot"
        self.emoji = ":target:"
        # When we instantiate a new bot object, we can access the app
        # credentials we set earlier in our local development environment.
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                      "client_secret": os.environ.get("CLIENT_SECRET"),
                      # Scopes provide and limit permissions to what our app
                      # can access. It's important to use the most restricted
                      # scope that your app will need.
                      "scope": "bot"}
        self.verification = os.environ.get("VERIFICATION_TOKEN")

        # NOTE: Python-slack requires a client connection to generate
        # an oauth token. We can connect to the client without authenticating
        # by passing an empty string as a token and then reinstantiating the
        # client with a valid OAuth token once we have one.
        self.client = SlackClient("")
        # We'll use this dictionary to store the state of each message object.
        # In a production environment you'll likely want to store this more
        # persistantly in a database.
        self.messages = {}


    def auth(self, code):
        """
        Authenticate with OAuth and assign correct scopes.
        Save a dictionary of authed team information in memory on the bot
        object.

        Parameters
        ----------
        code : str
            temporary authorization code sent by Slack to be exchanged for an
            OAuth token

        """
        # After the user has authorized this app for use in their Slack team,
        # Slack returns a temporary authorization code that we'll exchange for
        # an OAuth token using the oauth.access endpoint
        auth_response = self.client.api_call(
                                "oauth.access",
                                client_id=self.oauth["client_id"],
                                client_secret=self.oauth["client_secret"],
                                code=code
                                )
        # To keep track of authorized teams and their associated OAuth tokens,
        # we will save the team ID and bot tokens to the global
        # authed_teams object
        team_id = auth_response["team_id"]
        authed_teams[team_id] = {"bot_token":
                                auth_response["bot"]["bot_access_token"]}
        # Then we'll reconnect to the Slack Client with the correct team's 
        # bot token
        self.client = SlackClient(authed_teams[team_id]["bot_token"])


    def open_dm(self, user_id):
        """
        Open a DM to send a welcome message when a 'team_join' event is
        recieved from Slack.

        Parameters
        ----------
        user_id : str
            id of the Slack user associated with the 'team_join' event

        Returns
        ----------
        dm_id : str
            id of the DM channel opened by this method
        """
        new_dm = self.client.api_call("im.open",
                                      user=user_id)
        print(new_dm)
        dm_id = new_dm["channel"]["id"]
        return dm_id


    def ask_question(self, user_id, message_name):
        """
        Create and send a message to a user.

        Parameters
        ----------
        user_id : str
            id of the Slack user associated with the incoming event

        """
        message_obj = message.Message()
        message_obj.channel = self.open_dm(user_id)
        message_obj.create_attachments(message_name + '.json')
        self.client.api_call("chat.postMessage",
            channel=message_obj.channel,
            username=self.name,
            icon_emoji=self.emoji,
            text=message_obj.text,
            attachments=message_obj.attachments
        )


    def check_welcome(self, user_id):
        # if price is already set skip, else
        # if cafe is set send price
        # else send cafe
        channel = self.open_dm(user_id)
        self.message_user(channel, "Welcome to the Target Slack!")
        self.message_user(channel, ("I'm your friendly neighborhood cafe bot, "
                                    "and I deliver the cafeteria menu straight here daily"))
        self.message_user(channel, ("Choose your settings to get started!\n"
                                    "(You'll be able to change these at any time)."))
        self.ask_question(user_id, "/messages/cafe_message")


    def format_message(self, menu, price):
        message = ""
        for meal in menu.meals:
            message += "*" + meal.name.upper() + "*\n"
            for station in meal.stations:
                message += (meal.stations[station].name).title() + "\n"
                for special in meal.stations[station].specials:
                    item = ">" + special["label"].title()
                    if price:
                        item += '.'*(100 - len(item) - len(special["price"])) + special["price"]
                    message += item + "\n"
        return message


    def send_menu(self):
        ids = db.get_user_ids()
        for user_id in ids:
            print(str(user_id) + "\n")
            cafe_name = db.get_cafe_setting(user_id)
            price = db.get_price_setting(user_id)
            menu = cafe.get_menu(cafe_name)
            text = self.format_message(menu, price)
            channel = self.open_dm(user_id)
            self.message_user(channel, text)
        

    def process_selection(self, user_id, callback_id, text_name, val_selected, channel, ts):
        # update message
        question = ""
        if (callback_id == "cafe_name"):
            question = "Default Cafeteria:"
        else:
            question = "Display Item Prices?"
        self.client.api_call( "chat.update",
            channel = channel,
            ts = ts,
            text = question,
            attachments=[
                {
                    "text": "You chose: " + text_name,
                    "attachment_type": "default",
                    "color": "good"
                }
            ]
        )
        # Brief pause
        time.sleep(1)
        # save choice, if choice = cafe then send next question, else thanks message
        if callback_id == "cafe_name":
            db.put_cafe_setting(user_id, val_selected)
            self.ask_question(user_id, "/messages/price_message")

        if callback_id == "price_check":
            db.put_price_setting(user_id, val_selected)
            self.client.api_call( "chat.postMessage",
                channel = channel,
                username=self.name,
                icon_emoji=self.emoji,
                text="Thanks! I'll update your preferences now. Look forward to a daily menu!",
            )
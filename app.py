# -*- coding: utf-8 -*-
"""
Python Slack app modified from the Slack pythOnBoarding app
"""
import json
import bot
from flask import Flask, request, make_response, render_template, g
import threading
import time
import requests
import schedule

pyBot = bot.Bot()
slack = pyBot.client

app = Flask(__name__)


def _event_handler(event_type, slack_event):
    """
    A helper function that routes events from Slack to our Bot
    by event type and subtype.

    Parameters
    ----------
    event_type : str
        type of event recieved from Slack
    slack_event : dict
        JSON response from a Slack reaction event

    Returns
    ----------
    obj
        Response object with 200 - ok or 500 - No Event Handler error

    """

    """
    # Test basic message to bot
    if event_type == "message" and not slack_event["event"].get("subtype"):
        user_id = slack_event["event"]["user"]
        pyBot.message_user(user_id)
        return make_response("Message Sent", 200)
    """

    # ================ Team Join Events =============== #
    # When the user first joins a team, the type of event will be team_join
    if event_type == "team_join":
        user_id = slack_event["event"]["user"]
        # Send the onboarding message
        pyBot.check_welcome(user_id)
        return make_response("Welcome Message Sent", 200,)

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})

"""
# Need to visit site once before "beforefirstrequest" will activate
# - Call start_runner() before app.run
# Currently seems that's not the case but will leave code here for now
def start_runner():
    def start_loop():
        not_started = True
        while not_started:
            # print('In start loop')
            try:
                time.sleep(35)
                r = requests.get('http://127.0.0.1:5000/')
                if r.status_code == 200:
                    # print('Server started, quitting start_loop')
                    not_started = False
                    print("Server started")
                print(r.status_code)
            except:
                print('Server not yet started')
            time.sleep(10)

    # print('Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()
"""

@app.before_first_request
def activate_job():
    def run_job():
        while True:
            time.sleep(45)
            with app.app_context():
                pyBot.send_menu()
            #schedule.every().day.at("15:57").do(pyBot.send_menu)
            time.sleep(1000000)

    thread = threading.Thread(target=run_job)
    thread.start()

@app.route("/")
def hello():
    return "Hello All"

@app.route("/install", methods=["GET"])
def pre_install():
    """This route renders the installation page with 'Add to Slack' button."""
    # Since we've set the client ID and scope on our Bot object, we can change
    # them more easily while we're developing our app.
    client_id = pyBot.oauth["client_id"]
    scope = pyBot.oauth["scope"]
    # Our template is using the Jinja templating language to dynamically pass
    # our client id and scope
    return render_template("install.html", client_id=client_id, scope=scope)


@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    """
    This route is called by Slack after the user installs our app. It will
    exchange the temporary authorization code Slack sends for an OAuth token
    which we'll save on the bot object to use later.
    To let the user know what's happened it will also render a thank you page.
    """
    # Let's grab that temporary authorization code Slack's sent us from
    # the request's parameters.
    code_arg = request.args.get('code')
    # The bot's auth method to handles exchanging the code for an OAuth token
    pyBot.auth(code_arg)
    return render_template("thanks.html")

@app.route("/interactive", methods=["GET", "POST"])
def respond():
    form_json = json.loads(request.form["payload"])

    # Bot should handle all of this logic - so pass all info to bot
    # Check to see what the user's selection was and update the message
    user_id = form_json["user"]["id"]
    callback_id = form_json["callback_id"]
    name = form_json["actions"][0]["name"]
    val_selected = form_json["actions"][0]["value"]
    channel=form_json["channel"]["id"]
    ts = form_json["message_ts"]
    pyBot.process_selection(user_id, callback_id, name, val_selected, channel, ts)

    return make_response("", 200)


@app.route("/listening", methods=["GET", "POST"])
def hears():
    """
    This route listens for incoming events from Slack and uses the event
    handler helper function to route events to our Bot.
    """
    slack_event = json.loads(request.data)

    # ============= Slack URL Verification ============ #
    # In order to verify the url of our endpoint, Slack will send a challenge
    # token in a request and check for this token in the response our endpoint
    # sends back.
    #       For more info: https://api.slack.com/events/url_verification
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                             })
    
    # ============ Slack Token Verification =========== #
    # We can verify the request is coming from Slack by checking that the
    # verification token in the request matches our app's settings
    if pyBot.verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \npyBot has: \
                   %s\n\n" % (slack_event["token"], pyBot.verification)
        # By adding "X-Slack-No-Retry" : 1 to our response headers, we turn off
        # Slack's automatic retries during development.
        make_response(message, 403, {"X-Slack-No-Retry": 1})
    
    # ====== Process Incoming Events from Slack ======= #
    # If the incoming request is an Event we've subcribed to
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        # Then handle the event by event_type and have your bot respond
        return _event_handler(event_type, slack_event)
    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})

@app.teardown_appcontext
def close_connection(exception):
    """
    This is called when the request has been handled to make sure the database 
    connection closes/flushes. 
    See this example for more details: http://flask.pocoo.org/docs/0.12/patterns/sqlite3/
    :param exception: n/a
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    app.run(debug=True)
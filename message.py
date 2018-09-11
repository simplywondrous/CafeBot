# -*- coding: utf-8 -*-
"""
Python Slack Message class
"""
import yaml


class Message(object):
    """
    Instantiates a Message object to create and manage
    Slack onboarding messages.
    """
    def __init__(self):
        super(Message, self).__init__()
        self.channel = ""
        self.timestamp = ""
        self.text = ""
        self.attachments = []

    def create_attachments(self, file):
        """
        Open JSON message attachments file and create attachments for
        onboarding message. Saves a dictionary of formatted attachments on
        the bot object.
        """
        with open(file) as json_file:
            json_dict = yaml.safe_load(json_file)
            json_attachments = json_dict["attachments"]
            [self.attachments[i].update(json_attachments[i]) for i
             in range(len(json_attachments))]

# Class to handle the notification email.

import smtplib


class EmailMessage():


    # TODO add sending time, timezone in the constructor
    def __init__(self, email_list):
        self.email_list = email_list
        self.reportEntries = []


    def addRecord(self, report):
        self.reportEntries.append(report)
        pass



    def sendIfNotEmpty(self):
        if len(self.reportEntries) == 0: return

        message = self.createEmailMessage()


    def createEmailMessage(self):
        return "This will be the contents of the message."









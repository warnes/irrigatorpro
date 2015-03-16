# Class to handle the notification email.

import smtplib
from tabulate import tabulate
from datetime import date
from email.mime.text import MIMEText

class EmailListEmpty(Exception): pass

class EmailMessage():


    # TODO add sending time, timezone in the constructor
    def __init__(self, email_list):
        if len(email_list) == 0:
            raise(EmailListEmpty)
        self.email_list = email_list
        self.reportEntries = []


    def addRecord(self, report):
        self.reportEntries.append(report)
        pass



    def sendIfNotEmpty(self):
        if len(self.reportEntries) == 0: 
            return
        print "Will send email to ", len(self.email_list), " users"

        server = smtplib.SMTP('localhost')
        msg = MIMEText(self.createEmailMessage())
        msg['Subject'] = "Daily report for " + date.today().isoformat()
        msg['from'] = 'admin@irrigatorpro.org'
        msg['to'] = ','.join(self.email_list)

        s = smtplib.SMTP('mail.twc.com', 587)
        print 'sending email'
        s.sendmail('admin@irrigatorpro.org', self.email_list, msg.as_string())
        print 'done'
        s.quit()

        

        


    def createEmailMessage(self):

        table = []

        for report in self.reportEntries:
            table.append([
                report.field,
                report.crop,
                report.growth_stage,
                'Status here',
                report.message])



        return tabulate(table, headers = ['Field', 'Crop', 'Growth Stage', 'Status', 'Message'])

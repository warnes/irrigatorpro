# Class to handle the notification email.

from irrigator_pro.settings import NOTIFICATION_SMTP, NOTIFICATION_HOST, NOTIFICATION_PORT
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

        msg = MIMEText(self.createEmailMessage(), 'html')
        msg['Subject'] = "Daily report for " + date.today().isoformat()
        msg['from'] = 'admin@irrigatorpro.org'
        msg['to'] = ','.join(self.email_list)

        s = smtplib.SMTP(NOTIFICATION_SMTP, NOTIFICATION_PORT)
        print 'sending email'
        s.sendmail('admin@irrigatorpro.org', self.email_list, msg.as_string())
        print 'done'
        s.quit()



    def getStatus(self, report):
        if report.water_register_object.dry_down_flag == True:
            return report.water_register_object.status
        if (report.days_to_irrigation == 0):
            return "Irrigate Today"
        if (report.days_to_irrigation == 1):
            return "Irrigate Tomorrow"
        
        if (report.days_to_irrigation > 1):
            return "Irrigate in " + str(report.days_to_irrigation) + " Days"
        return ""
        
        
        

    def createEmailMessage(self):

        tableHeader = "<table style='border:1px'><thead>";
        headers = "";
        for h in ['Field', 'Crop', 'Growth Stage', 'Status', 'Message']:
            

        
        ret = "<style>table{border:1px;} </style>"
        ret += "This is and abbreviated daily report for " + date.today().isoformat()
        ret += "\n If you want a more detailed report you can follow this link: "
        ret += NOTIFICATION_HOST
        ret += "\n"

        table = []

        for report in self.reportEntries:
            table.append([
                report.field,
                report.crop,
                report.growth_stage,
                self.getStatus(report),
                report.message])



        return ret + "\n\n" + tabulate(table, headers = ['Field', 'Crop', 'Growth Stage', 'Status', 'Message'], tablefmt="html" )

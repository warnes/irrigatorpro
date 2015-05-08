# Class to handle the notification email.

from irrigator_pro.settings import NOTIFICATION_SMTP, NOTIFICATION_HOST, NOTIFICATION_PORT
import smtplib

from tabulate import tabulate  # Still needed?
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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



        #   msg = MIMEText(self.createEmailMessage(), 'html')
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Daily report for " + date.today().isoformat()
        msg['from'] = 'admin@irrigatorpro.org'
        msg['to'] = ','.join(self.email_list)

        htmlPart = self.createEmailMessage()
        textPart = "Here is the daily report"

        part1 = MIMEText(textPart, 'plain')
        part2 = MIMEText(htmlPart, 'html')

        msg.attach(part1)
        msg.attach(part2)
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


        topText = "<html><body>This is and abbreviated daily report for " + date.today().isoformat() + "<br/>If you want a more detailed report you can follow this link: <a href= \"" + NOTIFICATION_HOST + "\">daily report </a><br/><br/>"

        tableHeader = "<table style = 'border: 1px solid black; border-collapse: collapse;'>";
        headers = "<thead><row style = 'border: 1px solid black;'>";
        
        for h in ['Field', 'Crop', 'Growth Stage', 'Status', 'Message']:
            headers += ("<th style = 'border: 1px solid black;' >" + h + "</th>")
        headers += "</row></thead>"
        
        rows = "<tbody>"
        
        for report in self.reportEntries:
            rows += "<tr style = 'border: 1px solid black;'>"
            for cell in [
                report.field,
                report.crop,
                report.growth_stage,
                self.getStatus(report),
                report.message]:
                rows += ("<td style = 'border: 1px solid black;'>" + str(cell) + "</td>")
            rows += "</tr>"

        tableEnd = "</tbody></table></body></html>"

        print topText, "\n", tableHeader , "\n",  headers , "\n",  rows , "\n",  tableEnd

        return topText + tableHeader + headers + rows + tableEnd


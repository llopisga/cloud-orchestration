#!/usr/bin/python3
# coding=utf-8
import os
from email.message import EmailMessage
import logging
import logging.handlers


class errorEmail(logging.handlers.SMTPHandler):
    def emit(self, record):

        import smtplib
        from email.utils import formatdate

        msg = self.format(record)
        msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
            self.fromaddr,
            ",".join(self.toaddrs),
            self.getSubject(record),
            formatdate(), msg)
        smtp = smtplib.SMTP(self.mailhost, self.mailport)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        # Environment variables from master node server
        smtp.login(self.username, self.password)
        smtp.sendmail(self.fromaddr, self.toaddrs, msg)
        smtp.quit()


class sendEmail():
    def __init__(self, SMTP_SERVER, SMTP_PORT, FROM, TO, SUBJ, MSG, AUTH_USER, AUTH_TOKEN):
        self.SMTP_SERVER = SMTP_SERVER
        self.SMTP_PORT = SMTP_PORT
        self.FROM = FROM
        self.TO = TO
        self.SUBJ = SUBJ
        self.MSG = MSG
        self.AUTH_USER = AUTH_USER
        self.AUTH_TOKEN = AUTH_TOKEN

    def send(self):
        import smtplib
        from email.message import EmailMessage
        email = EmailMessage()
        email['Subject'] = self.SUBJ
        email['From'] = self.FROM
        email['To'] = self.TO
        email.set_content(self.MSG)
        smtp = smtplib.SMTP(host=self.SMTP_SERVER, port=self.SMTP_PORT)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        # Environment variables from master node server
        smtp.login(self.AUTH_USER, self.AUTH_TOKEN)
        smtp.send_message(email)
        smtp.quit()


class sendComplete():
    def __init__(self, SMTP_SERVER, SMTP_PORT, FROM, TO, SUBJ, MSG, AUTH_USER, AUTH_TOKEN, FILE):
        self.SMTP_SERVER = SMTP_SERVER
        self.SMTP_PORT = SMTP_PORT
        self.FROM = FROM
        self.TO = TO
        self.SUBJ = SUBJ
        self.MSG = MSG
        self.AUTH_USER = AUTH_USER
        self.AUTH_TOKEN = AUTH_TOKEN
        self.FILE = FILE

    def send(self):
        import smtplib
        from email.message import EmailMessage
        email = EmailMessage()
        email['Subject'] = self.SUBJ
        email['From'] = self.FROM
        email['To'] = self.TO
        email.set_content(self.MSG)
        with open(self.FILE, 'rb') as content_file:
            content = content_file.read()
            email.add_attachment(content, maintype='application/pdf', subtype='pdf', filename='access_details')
        smtp = smtplib.SMTP(host=self.SMTP_SERVER, port=self.SMTP_PORT)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        # Environment variables from master node server
        smtp.login(self.AUTH_USER, self.AUTH_TOKEN)
        smtp.send_message(email)
        smtp.quit()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os


import smtplib
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import formatdate


# Mail Account
MAIL_ACCOUNT = os.getenv('MAIL_ACCOUNT')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')


#SENDER_NAME = 'alerts'
SENDER_NAME = MAIL_ACCOUNT

# Mail Server
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
# TLS
SMTP_TLS = True
def send_mail(recipient, subject, body, encoding='utf-8'):
    session = None
    msg = MIMEText(body, 'plain', encoding)
    msg['Subject'] = Header(subject, encoding)
    msg['From'] = Header(SENDER_NAME, encoding)
    msg['To'] = recipient
    msg['Date'] = formatdate()
    try:
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        if SMTP_TLS:
            session.ehlo()
            session.starttls()
            session.ehlo()
            session.login(MAIL_ACCOUNT, MAIL_PASSWORD)
        session.sendmail(MAIL_ACCOUNT, recipient, msg.as_string())
    except Exception as e:
        raise e
    finally:
        # close session
        if session:
            session.quit()


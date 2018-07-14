# -*- coding: utf-8 -*-
'''
Sends daily reports via email
'''

import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from sensitive import emailcredentials

user, password, imap_url = emailcredentials()

def send_mail(send_from, send_to, subject, text, files=None) :
    assert isinstance(send_to, list)
    
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)
    try:
        smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp.ehlo()
        smtp.login(user, password)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.close()
    except :
        print('Something went wrong...')
    
send_mail(user,['kylejlynch@gmail.com'],'test email','This is an automated email. If you have any questions or concerns please email Kyle Lynch at kylejlynch@gmail.com',['timeblock_yesterday.png'])
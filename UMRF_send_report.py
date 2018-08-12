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
import pandas as pd

pd.set_option('display.max_columns', 100)
user, password, imap_url = emailcredentials()

def send_mail(send_from, send_to, subject, text, html=None, files=None) :
    assert isinstance(send_to, list)
    
    if html is None :
        html = ''
    else :
        html = html
    
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    
    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part2)
    msg.attach(part1)
    try:
        smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp.ehlo()
        smtp.login(user, password)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.close()
    except :
        print('Something went wrong...')

dfhtml = pd.read_html('ticket_percent_yest.html')[0]
dfhtml = dfhtml.drop(columns=['Unnamed: 0'])

text = 'This is an automated email. If you have any questions or concerns please email Kyle Lynch at kylejlynch@gmail.com'
html = dfhtml.to_html(index=False,border='border')
#emaillist = ['kylejlynch@gmail.com','jsankhon@umrfventures.com','chloe.sutton.osv@fedex.com','jemario.houston.osv@fedex.com','nedra.stratton.osv@fedex.com']
#send_mail(user, emaillist,'Ticket Percentage Less than 100%', text=text, html=html)
send_mail(user,['kylejlynch@gmail.com'],'test email', text,html=html,files=['timeblock_yesterday.png'])
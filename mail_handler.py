import os
import smtplib
import logging
import threading
from email.Utils import formatdate
from email.mime.text import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email import Encoders

threads = []

f = open("data","r")
user_name = f.readline()[:-1]
pass_word = f.readline()
f.close()

def clean_threads(threads=threads):
    ctrl = 0
    for t in threads:
        if t.isAlive():
            ctrl += 1
    if ctrl == 0:
        return []
    else:
        return threads

def send_mail(para, titulo, contenido, adjuntos=[]):
    msg = MIMEMultipart()
    msg['Subject'] = titulo
    msg['From'] = user_name
    msg['Date'] = formatdate(localtime=True)
    msg['To'] = para
    msg.attach( MIMEText(contenido) )
    # Attaching the file
    if len(adjuntos) != 0:
        for item in adjuntos:
            if item in os.listdir('.'):
                logging.info('Output file found! Processing ...')
                results = open(item,'r').read()
                part = MIMEBase('application', "octet-stream")
                part.set_payload( results )
                Encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(item))
                msg.attach(part)
            else:
                logging.warning('Output file not found.')
                results = "The input file had errors and no output coulf be generated."
    try:
        logging.info('Trying to establish connection through SMTP.')
        s = smtplib.SMTP('smtp.gmail.com',587)
        s.ehlo()
        s.starttls()
        s.ehlo
        s.login(user_name, pass_word)
        s.sendmail(user_name, [para], msg.as_string())
        s.quit()
        logging.info('email sent to: ' + para)
    except Exception as e:
        logging.error('Connection failed! email was not sent.')
        logging.error(e)

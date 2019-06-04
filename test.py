
import smtplib
# Import the email modules we'll need
from email.message import EmailMessage

HOST = "mail.it2g.ru"
SMTP = 'eps-relay01.mos.ru'
PORT = 25
USER = 'APKUMS'
PASSWD = 'J5?8T@y?'

FROM = "hd-usdpm@mos.ru"
#TO = "aidarovas@it2g.ru"
#TO2 = "bazhanovav@it2g.ru"
#TO3 = "gushchinyv@it2g.ru"
SUBJECT = "Будь осторожен"
TEXT = "МЫ СЛЕДИМ ЗА ТОБОЙ"

# Create a text/plain message
msg = EmailMessage()
msg.set_content(TEXT)

msg['Subject'] = SUBJECT
msg['From'] = FROM
msg['To'] = TO3

# Send the message via our own SMTP server.
with smtplib.SMTP(HOST) as s:
    s.send_message(msg)
    s.quit()

'''
with smtplib.SMTP_SSL(HOST, port, context=context) as server:
    server.login(FROM, password)
'''
import smtplib
# Import the email modules we'll need
import ssl
from email.message import EmailMessage

import csv

#HOST = "mail.it2g.ru"  # OMG HOST
SMTP = 'eps-relay01.mos.ru'
PORT = 25       # 587 for gmail\mail.ru
USER = 'APKUMS'
PASSWD = 'J5?8T@y?'

FROM = "hd-usdpm@mos.ru"
TO = "bazhanovav@it2g.ru"

SUBJECT = "Тестовая рассылка"
TEXT = "Уважаемые коллеги!\r\n" \
       "\r\nИнформируем о том, что Вам предоставлен доступ к Информационной системе Управление согласованием документов Правительства Москвы (ИС УСД ПМ).\r\n" \
       "\r\nСистема размещена в корпоративной сети по адресу: https://usd.mos.ru/\r\n" \
       "\r\nДля входа в систему необходимо:" \
       "\r\n   1. В адресной строке браузера (Google chrome или Яндекс браузер) введите адрес: https://usd.mos.ru" \
       "\r\n   2. Начните вводить свои ФИО в поле Пользователь" \
       "\r\n   3. Введите временный пароль: Qwerty123$$" \
       "\r\n   4. Придумайте новый пароль и укажите его дважды в соответствующие поля\r\n" \
       "\r\nОбучающие материалы размещены по адресу: https://yadi.sk/d/rVkIKjGXm2Ymzg\r\n" \
       "\r\nСистема функционирует в «пилотном» режиме, просим о всех недостатках или проблемах," \
       " связанных с работой системы сообщать в службу технической поддержки:\r\n" \
       "\r\nТелефон: +7 (499) 551-57-88" \
       "\r\nE-mail (круглосуточно): hd-usdpm@mos.ru\r\n" \
       "\r\nС уважением," \
       "\r\nСлужба технической поддержки ИС УСД ПМ."

HTML = """\
<html>
	<head>
		<style>

		</style>
	</head>
	<body lang=RU link=blue vlink="#954F72" style='tab-interval:35.4pt'>
		<div>
			<p><span>Уважаемые коллеги!</span></p>
			<p><span>Информируем о том, что Вам предоставлен доступ к Информационной системе Управление согласованием документов Правительства Москвы (ИС УСД ПМ).</span></p>
			<p><span>Система размещена в корпоративной сети по адресу: <a href="https://usd.mos.ru/">https://usd.mos.ru</a></span></p>
			<p><span>Для входа в систему необходимо:</span></p>
			<p><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 1. В адресной строке браузера (Google chrome или Яндекс браузер) введите адрес: <a href="https://usd.mos.ru/">https://usd.mos.ru</a></span></p>
			<p><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 2. Начните вводить свои ФИО в поле Пользователь</span></p>
			<p><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 3. Введите временный пароль: Qwerty123$$</span></p>
			<p><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 4. Придумайте новый пароль и укажите его дважды в соответствующие поля</span></p>
			<p><span>Обучающие материалы размещены по адресу: <a href="https://yadi.sk/d/rVkIKjGXm2Ymzg">https://yadi.sk/d/rVkIKjGXm2Ymzg</a></span></p>
			<p><span>Система функционирует в «пилотном» режиме, просим о всех недостатках или проблемах, связанных с работой системы сообщать в службу технической поддержки:</span></p>
			<p><span>Телефон: +7 (499) 551-57-88</span></p>
			<p><span>E-mail (круглосуточно):<a href="tel:+74995515788">hd-usdpm@mos.ru</a></span></p>
			<p><span>С уважением,</span></p>
			<p><span>Служба технической поддержки ИС УСД ПМ.</span></p>
		</div>
	</body>
</html>
"""


# Create a text/plain message
msg = EmailMessage()
msg.set_content(TEXT)

msg.add_alternative(HTML, subtype='html')

msg['Subject'] = SUBJECT
msg['From'] = FROM
msg['To'] = TO

'''
# Send the message via our own SMTP server.
with smtplib.SMTP(HOST) as s:
    s.send_message(msg)
    s.quit()
'''

#context = ssl.create_default_context()
#context = ssl.SSLContext()
#context.verify_mode = ssl.CERT_NONE     # CERT_NONE, CERT_OPTIONAL, CERT_REQUIRED
#context.check_hostname = True

try:
    server = smtplib.SMTP(SMTP, PORT)
    server.set_debuglevel(1)
    print('1')
    server.connect(SMTP, PORT)
    print('2')
    context = ssl.SSLContext()
    server.starttls(keyfile=None, certfile=None, context=context)
    print('3')
    server.ehlo()
#    server.send('AUTH NTLM LOGIN\r\n')
#    server.ehlo()
#    server.send('QVBLVU1T\r\n')
#    server.send('SjU/OFRAeT8=')
    server.login(user, password)
#    server.has_extn('NTLM')
    print('4')
#    server.sendmail(fromaddr, toaddr, msg)
    server.send_message(msg, from_addr=fromaddr, to_addrs=toaddr, mail_options=(), rcpt_options=('NOTIFY=SUCCESS,DELAY,FAILURE'))
    print('5')
#    server.quit()
except Exception as e:
    print(e)

''' SMTP END '''

'''
SEND IT2G

import smtplib
from email.message import EmailMessage

# Create a text/plain message
msg = EmailMessage()
msg.set_content("МЫ СЛЕДИМ ЗА ТОБОЙ")

msg['Subject'] = "Будь осторожен"
msg['From'] = "bazhanovav@it2g.ru" # Any address
msg['To'] = "bazhanovav@it2g.ru"   # Any address

# Send the message via our SMTP server.
with smtplib.SMTP("mail.it2g.ru") as s:
    s.send_message(msg)
    s.quit()

'''
with smtplib.SMTP_SSL(HOST, port, context=context) as server:
    server.login(FROM, password)
'''

'''
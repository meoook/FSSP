'''


import csv, smtplib, ssl

message = """Subject: Your grade

Hi {name}, your grade is {grade}"""
from_address = "my@gmail.com"
password = input("Type your password and press enter: ")

context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(from_address, password)
    with open("contacts_file.csv") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for name, email, grade in reader:
            server.sendmail(
                from_address,
                email,
                message.format(name=name,grade=grade),
            )





import csv

with open("C:\tmp\mail.txt") as file:
    reader = csv.reader(file)
    next(reader)  # Skip header row
    for email, name, lastname in reader:
        print(f"Sending email to {name}")
        server.sendmail(
                from_address,
                email,
                message.format(name=name,lastname=lastname),
            )


For example, "hi {name}, you {result} your assignment".format(name="John", result="passed") will give you "hi John, you passed your assignment".
https://docs.python.org/3/library/email.examples.html#email-examples
'''


import smtplib
# Import the email modules we'll need
from email.message import EmailMessage

import csv

#HOST = "mail.it2g.ru"
SMTP = 'eps-relay01.mos.ru'
PORT = 25
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
with smtplib.SMTP(SMTP, PORT) as s:
    s.set_debuglevel(1)
    s.send_message(msg, FROM, TO)
    '''
    with open(r"C:\tmp\mail.txt") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for email, name, lastname in reader:
            print(f"Sending email to {name}")
            msg = EmailMessage()
            msg.set_content(TEXT)

            msg.add_alternative(HTML, subtype='html')

            msg['Subject'] = SUBJECT
            msg['From'] = FROM
            msg['To'] = email
'''

    s.quit()
'''
with smtplib.SMTP_SSL(HOST, port, context=context) as server:
    server.login(FROM, password)
'''
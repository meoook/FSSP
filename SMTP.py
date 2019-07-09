import smtplib
#from email.message import EmailMessage
import email

'''
SMTP = 10.89.65.20
helo 'mos.ru"
port 25
starttls on
user\password
APKUMS
'''

HOST = "mail.it2g.ru"  # OMG HOST
SMTP = 'eps-relay01.mos.ru'
PORT = 25       # 587 for gmail\mail.ru
USER = 'APKUMS'
PASSWD = 'J5?8T@y?'

TEXT = "Уважаемые коллеги!\r\n" \


HTML = """
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
SUBJECT = "Тестовая рассылка"

#FROM = "hd-usdpm@mos.ru"
FROM = "hd-ums@mos.ru"
TO = "bazhanovav@it2g.ru"

FROM2 = "info@it2g.ru"
TO2 = "mmurz@mail.ru"

TO3 = "gushchinyv@it2g.ru"


# Create a text/plain message
msg = email.message.EmailMessage()
msg.set_content(TEXT)
# Create a HTML message
msg.add_alternative(HTML, subtype='html')
# Other mail params
msg['Subject'] = SUBJECT
msg['From'] = FROM
msg['To'] = TO


# Send the message via SMTP server.
with smtplib.SMTP(SMTP) as s:
    s.set_debuglevel(1)
#    s.starttls()
#    s.login("bazhanovav@it2g.ru", "pass")
    s.send_message(msg)
    s.quit()



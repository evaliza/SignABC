from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

class Email():
    def sendMail(subject, message):
        msg = MIMEMultipart()
        msg['From'] = 'ilizaeve@gmail.com'
        msg['To'] = 'ilizaeve@gmail.com'
        msg['Subject'] = subject
        message = message
        msg.attach(MIMEText(message))
        mailserver = smtplib.SMTP('smtp.gmail.com', 587)
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.ehlo()
        mailserver.login('ilizaeve@gmail.com', 'zjqp kvly rkue thfe')
        mailserver.sendmail('ilizaeve@gmail.com', 'ilizaeve@gmail.com', msg.as_string())
        mailserver.quit()
        pass